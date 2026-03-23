#!/usr/bin/env python3
"""
PERShtml 全自动更新脚本
- 自动扫描 S3 bucket 中的新 Excel 文件
- 记录已处理文件到 processed.log
- 只处理新文件，跳过已处理的
- 删除 processed.log 可强制重新处理
"""

import os
import sys
import subprocess
from datetime import datetime

# 配置
S3_BUCKET = 'persearlyaccess'
S3_PREFIX = 'Metadata/'
LOG_FILE = 'processed.log'

# AWS 凭证（从环境变量或 .env 读取）
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

def load_env_file():
    """加载 .env 文件"""
    env_file = '.env'
    if os.path.exists(env_file):
        print("📋 加载环境变量 (.env)")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_processed_files():
    """读取已处理的文件列表"""
    if not os.path.exists(LOG_FILE):
        return set()
    
    with open(LOG_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def mark_as_processed(filename):
    """标记文件为已处理"""
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{filename} # Processed at {timestamp}\n")

def list_s3_files():
    """列出 S3 bucket 中的所有 Excel 文件（使用 AWS CLI）"""
    try:
        # 使用 aws s3 ls 列出文件
        s3_path = f"s3://{S3_BUCKET}/{S3_PREFIX}"
        result = subprocess.run(
            ['aws', 's3', 'ls', s3_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 解析输出
        excel_files = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            # 格式: 2026-03-21 00:21:45      17998 26-04_April_metadata.xlsx
            parts = line.split()
            if len(parts) >= 4:
                filename = parts[3]
                if filename.endswith('.xlsx'):
                    excel_files.append(filename)
        
        return excel_files
    
    except subprocess.CalledProcessError as e:
        print(f"❌ AWS CLI 错误: {e.stderr if e.stderr else str(e)}")
        return []
    except Exception as e:
        print(f"❌ 无法列出 S3 文件: {e}")
        return []

def process_file(filename):
    """处理单个 Excel 文件"""
    print(f"\n{'='*70}")
    print(f"📥 处理: {filename}")
    print(f"{'='*70}")
    
    # 运行 update_from_s3.py
    try:
        result = subprocess.run(
            ['python3', 'update_from_s3.py', filename],
            capture_output=True,
            text=True
        )
        
        # 显示输出
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ 处理失败: {filename}")
            if result.stderr:
                print(result.stderr)
            return False
        
        print(f"✅ 处理完成: {filename}")
        return True
    
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    print("=" * 70)
    print("🦞 PERShtml 全自动更新")
    print("=" * 70)
    
    # 1. 加载环境变量
    load_env_file()
    
    # 检查 AWS 凭证
    if not os.environ.get('AWS_ACCESS_KEY_ID'):
        print("❌ 未找到 AWS 凭证")
        print("   请配置 .env 文件或设置环境变量")
        sys.exit(1)
    
    # 2. 读取已处理文件列表
    processed = get_processed_files()
    print(f"\n📋 已处理的文件数: {len(processed)}")
    if processed:
        print("   最近处理:")
        for f in list(processed)[-3:]:
            print(f"   - {f.split('#')[0].strip()}")
    
    # 3. 列出 S3 中的文件
    print(f"\n📡 扫描 S3 bucket: s3://{S3_BUCKET}/{S3_PREFIX}")
    s3_files = list_s3_files()
    
    if not s3_files:
        print("   未找到 Excel 文件")
        return
    
    print(f"   找到 {len(s3_files)} 个 Excel 文件")
    
    # 4. 找出新文件
    new_files = []
    for f in s3_files:
        # 检查是否已处理（log 中可能包含注释）
        if not any(f in line for line in processed):
            new_files.append(f)
    
    if not new_files:
        print("\n✅ 没有新文件需要处理")
        print("   所有文件都已处理过")
        print(f"\n💡 提示: 删除 {LOG_FILE} 可强制重新处理")
        return
    
    print(f"\n📌 发现 {len(new_files)} 个新文件:")
    for f in new_files:
        print(f"   - {f}")
    
    # 5. 处理每个新文件
    processed_count = 0
    failed_files = []
    
    for filename in new_files:
        success = process_file(filename)
        
        if success:
            mark_as_processed(filename)
            processed_count += 1
        else:
            failed_files.append(filename)
    
    # 6. 总结
    print("\n" + "=" * 70)
    print("📊 处理总结")
    print("=" * 70)
    print(f"✅ 成功处理: {processed_count} 个文件")
    if failed_files:
        print(f"❌ 失败: {len(failed_files)} 个文件")
        for f in failed_files:
            print(f"   - {f}")
    
    # 7. Git 提交（如果有成功处理的文件）
    if processed_count > 0:
        print("\n📦 提交到 Git...")
        try:
            # 检查是否有变化
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():
                # 有变化，提交
                subprocess.run(['git', 'add', '.'], check=True)
                
                commit_msg = f"Auto update: {', '.join(new_files[:3])}"
                if len(new_files) > 3:
                    commit_msg += f" and {len(new_files) - 3} more"
                
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                print("   ✅ Git commit 完成")
                
                # 询问是否推送
                print("\n💡 运行 'git push' 来推送到 GitHub")
            else:
                print("   ℹ️  没有变化需要提交")
        except Exception as e:
            print(f"   ⚠️  Git 操作失败: {e}")
    
    print("\n" + "=" * 70)
    print("✅ 自动更新完成")
    print("=" * 70)

if __name__ == '__main__':
    main()
