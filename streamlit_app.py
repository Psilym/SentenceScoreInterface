import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="句子级别评估系统 v2",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 设置页面宽度 */
    .main .block-container {
        max-width: 95%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    .sentence-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .original-sentence {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2c3e50;
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.375rem;
        border-left: 4px solid #1976d2;
        margin-bottom: 1rem;
    }
    
    .generated-sentence {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2c3e50;
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.375rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #495057;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #dee2e6;
        padding-bottom: 0.25rem;
    }
    
    .instruction-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 0.375rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #2196F3;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def load_excel_data(file_path):
    """从Excel文件加载数据，提取原始答案和生成答案"""
    try:
        df = pd.read_excel(file_path)
        
        # 检查必需的列
        required_cols = ['原始答案', '生成答案']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Excel文件缺少必需的列: {missing_cols}")
            return None
        
        # 转换数据格式
        sentences = []
        
        for idx, row in df.iterrows():
            # 优先使用中文，如果没有则使用英文
            original_answer = str(row.get('原始答案', '')).strip()
            if pd.isna(row.get('原始答案')) or not original_answer:
                original_answer = str(row.get('原始答案(英文)', '')).strip()
            
            generated_answer = str(row.get('生成答案(中文)', '')).strip()
            if pd.isna(row.get('生成答案(中文)')) or not generated_answer:
                generated_answer = str(row.get('生成答案', '')).strip()
            if pd.isna(row.get('生成答案')) or not generated_answer:
                generated_answer = str(row.get('生成答案(英文)', '')).strip()
            
            # 如果原始答案或生成答案为空，跳过
            if not original_answer or not generated_answer:
                continue
            
            # 收集其他信息
            sentence_data = {
                'original_answer': original_answer,
                'generated_answer': generated_answer,
                '模型来源': str(row.get('模型来源', '')),
                'row_idx': idx
            }
            
            sentences.append(sentence_data)
        
        return {
            'sentences': sentences,
            'source': 'excel',
            'total_rows': len(df),
            'total_sentences': len(sentences)
        }
        
    except Exception as e:
        st.error(f"Excel文件加载错误: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

def save_evaluation_results(username, results, batch_idx=None, output_dir="evaluation_results"):
    """保存评估结果"""
    if not username or not username.strip():
        raise ValueError("用户名不能为空")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if batch_idx is not None:
        filename = f"batch_{batch_idx}_{username}_{timestamp}.json"
    else:
        filename = f"evaluation_{username}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 准备保存的数据
    save_data = {
        "username": username,
        "timestamp": timestamp,
        "batch_idx": batch_idx,
        "results": results
    }
    
    # 保存到文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def main():
    st.markdown('<div class="main-header">📝 句子级别评估系统 v2</div>', unsafe_allow_html=True)
    
    # 初始化session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = {}  # 存储评估结果
    if 'current_batch' not in st.session_state:
        st.session_state.current_batch = 0
    if 'batch_saved' not in st.session_state:
        st.session_state.batch_saved = set()  # 记录已保存的批次

    batch_size = 5  # 每批次5个句子

    # 侧边栏 - 用户信息
    st.sidebar.header("👤 用户信息")
    username = st.sidebar.text_input(
        "用户名:",
        placeholder="请输入您的用户名",
        key="username_input"
    )
    
    # 侧边栏 - 文件加载
    st.sidebar.header("📁 数据加载")
    
    uploaded_file = st.sidebar.file_uploader(
        "上传文件（支持JSON或Excel）",
        type=['json', 'xlsx', 'xls'],
        help="请上传包含句子数据的JSON文件或Excel文件（merged_benchmark_result（正式版）.xlsx）"
    )
    
    if uploaded_file is not None:
        try:
            # 根据文件类型选择加载方式
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension in ['xlsx', 'xls']:
                # 加载Excel文件
                # 保存上传的文件到临时位置
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                data = load_excel_data(tmp_path)
                if data:
                    st.session_state.data = data
                    st.session_state.evaluation_results = {}
                    st.sidebar.success(f"✅ Excel文件加载成功！共 {data.get('total_sentences', 0)} 个句子")
                
                # 清理临时文件
                os.unlink(tmp_path)
            else:
                st.sidebar.error(f"❌ 不支持的文件格式: {file_extension}")
        except Exception as e:
            st.sidebar.error(f"❌ 文件加载失败: {e}")
            import traceback
            st.sidebar.error(traceback.format_exc())
    
    # 主界面
    if st.session_state.data is None:
        st.info("💡 请从侧边栏加载数据开始使用")
        return
    
    if not username or not username.strip():
        st.warning("⚠️ 请在侧边栏输入用户名后开始评估")
        return
    
    data = st.session_state.data
    
    # 检查数据格式
    if 'sentences' not in data:
        st.error("❌ 数据格式错误：缺少'sentences'字段")
        return
    
    sentences = data['sentences']
    total_sentences = len(sentences)
    
    # 计算批次信息
    total_batches = (total_sentences + batch_size - 1) // batch_size  # 向上取整
    
    # 侧边栏 - 批次选择
    st.sidebar.header("🔢 批次选择")
    st.sidebar.markdown(f"**总批次数:** {total_batches}")
    st.sidebar.markdown(f"**每批次:** {batch_size} 个句子")
    
    # 批次选择器
    batch_options = []
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_sentences)
        saved_mark = "✅" if i in st.session_state.batch_saved else "⏳"
        batch_options.append(f"{saved_mark} 批次 {i+1}")
    
    selected_batch_str = st.sidebar.selectbox(
        "选择批次:",
        batch_options,
        index=st.session_state.current_batch,
        key=f"batch_selector_{st.session_state.current_batch}"
    )
    
    # 解析选择的批次
    selected_batch = int(selected_batch_str.split("批次")[1].split("(")[0].strip()) - 1
    if selected_batch != st.session_state.current_batch:
        st.session_state.current_batch = selected_batch
        st.rerun()
    
    current_batch = st.session_state.current_batch
    
    # 计算当前批次的句子范围
    start_idx = current_batch * batch_size
    end_idx = min((current_batch + 1) * batch_size, total_sentences)
    batch_sentences = sentences[start_idx:end_idx]
    
    # 显示当前批次信息和说明
    col_info1, col_info2, col_info3 = st.columns([1, 1, 1])
    with col_info1:
        st.metric("当前批次", f"{current_batch + 1}/{total_batches}")
    with col_info2:
        st.metric("批次句子数", f"{len(batch_sentences)}")
    with col_info3:
        batch_completed = sum(1 for i in range(start_idx, end_idx) if i in st.session_state.evaluation_results)
        st.metric("已评估", f"{batch_completed}/{len(batch_sentences)}")
    
    # 显示说明
    st.markdown("""
    <div class="instruction-box">
        <strong>📋 使用说明：</strong>
        <ul>
            <li>左侧选择要处理的批次（每批次5个句子）</li>
            <li>每个卡片显示一个原始答案和生成答案的对比</li>
            <li>请为每个生成答案统计以下4类错误的数量：</li>
            <ol>
                <li><strong>预测错误</strong>：原报告没有，预测有（如原报告没有肺部阴影，预测有阴影）</li>
                <li><strong>缺失预测</strong>：原报告有，预测没有（如原报告有肺部结节，预测没有结节）</li>
                <li><strong>位置描述错误</strong>：不正确的位置描述（如原报告有左下肺阴影，预测右肺阴影）</li>
                <li><strong>严重程度错误</strong>：不正确的严重程度（如原报告严重胸膜粘连，预测轻度粘连）</li>
            </ol>
            <li>完成当前批次后，点击"下载批次"按钮保存结果</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 为当前批次的每个句子创建评估界面
    for local_idx, sentence_data in enumerate(batch_sentences):
        global_idx = start_idx + local_idx  # 全局索引
        original_answer = sentence_data.get('original_answer', '')
        generated_answer = sentence_data.get('generated_answer', '')
        row_idx = sentence_data.get('row_idx', None)
        
        # 创建卡片
        with st.container():
            st.markdown(f"### 句子 #{global_idx + 1} (批次内第 {local_idx + 1} 个)")
            
            # 显示原始答案
            st.markdown(f'<div class="original-sentence">原始答案: {original_answer}</div>', 
                       unsafe_allow_html=True)
            
            # 显示生成答案
            st.markdown(f'<div class="generated-sentence">生成答案: {generated_answer}</div>', 
                       unsafe_allow_html=True)
            
            # 显示指标（如果存在）
            metric_cols = ['bertscore_f1', 'bleu', 'cxrscore_har_score', 'rouge_l', 'meteor']
            available_metrics = {col: sentence_data.get(col) for col in metric_cols if col in sentence_data}
            if available_metrics:
                st.markdown("**评估指标:**")
                metric_display = ", ".join([f"{k}: {v:.4f}" for k, v in available_metrics.items()])
                st.markdown(metric_display)
            
            # 初始化当前句子的评估结果
            if global_idx not in st.session_state.evaluation_results:
                st.session_state.evaluation_results[global_idx] = {
                    'global_idx': global_idx,
                    'row_idx': row_idx,
                    'original_answer': original_answer,
                    'generated_answer': generated_answer,
                    'errors': {}
                }
            
            # 错误评估部分
            st.markdown('<div class="section-title">错误统计</div>', 
                       unsafe_allow_html=True)
            
            # 4个错误类型的计数输入
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                error1_key = f"error_{global_idx}_prediction_error"
                error1_count = st.number_input(
                    "1. 预测错误",
                    min_value=0,
                    value=int(st.session_state.evaluation_results[global_idx]['errors'].get('prediction_error', 0)),
                    key=error1_key,
                    help="原报告没有，预测有（如原报告没有肺部阴影，预测有阴影）"
                )
            
            with col2:
                error2_key = f"error_{global_idx}_missing_prediction"
                error2_count = st.number_input(
                    "2. 缺失预测",
                    min_value=0,
                    value=int(st.session_state.evaluation_results[global_idx]['errors'].get('missing_prediction', 0)),
                    key=error2_key,
                    help="原报告有，预测没有（如原报告有肺部结节，预测没有结节）"
                )
            
            with col3:
                error3_key = f"error_{global_idx}_location_error"
                error3_count = st.number_input(
                    "3. 位置描述错误",
                    min_value=0,
                    value=int(st.session_state.evaluation_results[global_idx]['errors'].get('location_error', 0)),
                    key=error3_key,
                    help="不正确的位置描述（如原报告有左下肺阴影，预测右肺阴影）"
                )
            
            with col4:
                error4_key = f"error_{global_idx}_severity_error"
                error4_count = st.number_input(
                    "4. 严重程度错误",
                    min_value=0,
                    value=int(st.session_state.evaluation_results[global_idx]['errors'].get('severity_error', 0)),
                    key=error4_key,
                    help="不正确的严重程度（如原报告严重胸膜粘连，预测轻度粘连）"
                )
            
            # 保存错误计数
            st.session_state.evaluation_results[global_idx]['errors']['prediction_error'] = error1_count
            st.session_state.evaluation_results[global_idx]['errors']['missing_prediction'] = error2_count
            st.session_state.evaluation_results[global_idx]['errors']['location_error'] = error3_count
            st.session_state.evaluation_results[global_idx]['errors']['severity_error'] = error4_count
            
            st.markdown("---")
    
    # 下载按钮
    st.markdown("### 💾 下载结果")
    
    _, col2, _ = st.columns([1, 1, 1])
    
    with col2:
        # 下载当前批次
        batch_results_dict = {k: v for k, v in st.session_state.evaluation_results.items() 
                             if start_idx <= k < end_idx}
        if batch_results_dict:
            # 将字典转换为数组，按global_idx排序
            batch_results = [v for k, v in sorted(batch_results_dict.items(), key=lambda x: x[0])]
            
            download_data = {
                "username": username,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "batch_idx": current_batch + 1,
                "batch_range": f"{start_idx}-{end_idx-1}",
                "error_types": {
                    "1": "预测错误",
                    "2": "缺失预测",
                    "3": "位置描述错误",
                    "4": "严重程度错误"
                },
                "results": batch_results
            }
            json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label=f"📥 下载批次 {current_batch + 1}",
                data=json_str,
                file_name=f"batch_{current_batch + 1}_usr_{username}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # 批次导航按钮
    st.markdown("---")
    st.markdown("### 🔄 批次导航")
    
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    
    with nav_col1:
        # 上一个批次按钮
        is_first_batch = current_batch <= 0
        if st.button("⬅️ 上一个批次", disabled=is_first_batch, use_container_width=True, key="prev_batch_btn"):
            st.session_state.current_batch = current_batch - 1
            st.rerun()
    
    with nav_col2:
        # 显示当前进度
        st.markdown(f"<div style='text-align: center; padding: 8px; background-color: #e3f2fd; border-radius: 5px;'>"
                   f"<strong>批次 {current_batch + 1} / {total_batches}</strong></div>", 
                   unsafe_allow_html=True)
    
    with nav_col3:
        # 下一个批次按钮
        is_last_batch = current_batch >= total_batches - 1
        if st.button("➡️ 下一个批次", disabled=is_last_batch, use_container_width=True, key="next_batch_btn"):
            st.session_state.current_batch = current_batch + 1
            st.rerun()

if __name__ == "__main__":
    main()

