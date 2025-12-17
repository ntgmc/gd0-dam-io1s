import streamlit as st
import json
import os
import hashlib
import copy
import time

# 尝试导入 logic 模块中的版本号，如果 logic.py 里没有定义 VERSION，则使用默认值
try:
    from logic import WorkplaceOptimizer
    from logic import VERSION as LOGIC_VERSION
except ImportError:
    from logic import WorkplaceOptimizer

    LOGIC_VERSION = "1.0.0"

# ==========================================
# 版本控制配置
# ==========================================
APP_VERSION = "1.1.0"  # 在此处修改前端 App 版本号

# ==========================================
# 0. 样式与配置
# ==========================================

st.set_page_config(page_title="MAA 基建排班售后服务", page_icon="💎", layout="wide")

st.markdown("""
<style>
/* 隐藏顶部菜单和页脚 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stAppHeader {display: none;}

/* 卡片样式 */
.user-card {
    padding: 20px;
    background-color: #f0f2f6;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* 强制隐藏右上角 */
.stAppHeader .stToolbarActions .stToolbarActionButton button,
[data-testid="stToolbarActionButtonIcon"],
.stAppHeader .stToolbarActions {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    gap: 0 !important;
}

/* 优化按钮样式 */
div.stButton > button:first-child {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. 工具函数
# ==========================================

def get_user_hash(order_id):
    return hashlib.sha256(order_id.strip().encode('utf-8')).hexdigest()[:16]


def load_user_data(user_hash):
    base_path = os.path.join("user_data", user_hash)
    ops_path = os.path.join(base_path, "operators.json")
    conf_path = os.path.join(base_path, "config.json")

    if os.path.exists(ops_path) and os.path.exists(conf_path):
        with open(ops_path, 'r', encoding='utf-8') as f:
            ops = json.load(f)
        with open(conf_path, 'r', encoding='utf-8') as f:
            conf = json.load(f)
        return ops, conf
    return None, None


def save_user_data(user_hash, ops_data):
    base_path = os.path.join("user_data", user_hash)
    ops_path = os.path.join(base_path, "operators.json")

    if os.path.exists(base_path):
        with open(ops_path, 'w', encoding='utf-8') as f:
            json.dump(ops_data, f, ensure_ascii=False, indent=2)
        return True
    return False


def upgrade_operator_in_memory(operators_data, char_id, char_name, target_elite):
    """内存修改干员练度"""
    target_id_str = str(char_id)
    for op in operators_data:
        current_id_str = str(op.get('id', ''))
        current_name = op.get('name', '')

        match = False
        if current_id_str and current_id_str == target_id_str:
            match = True
        elif current_name and current_name == char_name:
            match = True

        if match:
            op['elite'] = int(target_elite)
            op['level'] = 1  # 默认重置为1级，根据需求调整
            return True, f"{current_name}"

    return False, None


def clean_data(d):
    return {k: v for k, v in d.items() if k != 'raw_results'}


# ==========================================
# 2. 会话状态初始化
# ==========================================

if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'user_hash' not in st.session_state:
    st.session_state.user_hash = ""
if 'user_ops' not in st.session_state:
    st.session_state.user_ops = None
if 'user_conf' not in st.session_state:
    st.session_state.user_conf = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'list_version' not in st.session_state:
    st.session_state.list_version = 0
if 'final_result_ready' not in st.session_state:
    st.session_state.final_result_ready = False

# ==========================================
# 3. 登录页
# ==========================================

if not st.session_state.auth_status:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        # st.image(
        #     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Arknights_logo.svg/1200px-Arknights_logo.svg.png",
        #     width=150)
        st.markdown("<h2 style='text-align: center;'>💎 VIP 基建售后服务</h2>", unsafe_allow_html=True)

        with st.form("login_form"):
            order_id = st.text_input("请输入闲鱼订单号", placeholder="例如：36281xxxxxx")
            submitted = st.form_submit_button("验证身份", use_container_width=True)

            if submitted and order_id:
                u_hash = get_user_hash(order_id)
                ops, conf = load_user_data(u_hash)

                if ops and conf:
                    st.session_state.auth_status = True
                    st.session_state.user_hash = u_hash
                    st.session_state.user_ops = ops
                    st.session_state.user_conf = conf
                    st.toast("✅ 验证成功！", icon="🎉")
                    st.rerun()
                else:
                    st.error("❌ 未找到订单信息或服务已过期，请联系卖家。")

# ==========================================
# 4. 主功能区
# ==========================================

else:
    # --- 侧边栏 ---
    with st.sidebar:
        st.success(f"状态: 已登录")
        st.caption(f"ID: {st.session_state.user_hash[:8]}...")
        st.caption(f"配置: {st.session_state.user_conf.get('desc', 'Custom')}")

        st.divider()

        # --- 新增：版本信息显示 ---
        st.markdown(f"""
        <div style="
            display: flex; 
            justify-content: space-between; 
            color: #666; 
            font-size: 0.8rem;
            margin-bottom: 10px;
        ">
            <span>App: v{APP_VERSION}</span>
            <span>Logic: v{LOGIC_VERSION}</span>
        </div>
        """, unsafe_allow_html=True)
        # ------------------------

        if st.button("退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("🏭 智能排班生成器")

    # --- 逻辑控制区 ---

    # 临时文件路径定义
    temp_ops_path = f"temp_{st.session_state.user_hash}.json"
    temp_conf_path = f"temp_conf_{st.session_state.user_hash}.json"

    # 1. 自动运行分析 (如果是首次加载或数据已更新)
    if not st.session_state.analysis_done:
        with st.status("正在分析基建潜力...", expanded=True) as status:
            try:
                # 写入临时文件供算法读取
                with open(temp_ops_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_ops, f)
                with open(temp_conf_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_conf, f)

                # 调用核心算法
                optimizer = WorkplaceOptimizer("internal", temp_ops_path, temp_conf_path)
                curr = optimizer.get_optimal_assignments(ignore_elite=False)
                pot = optimizer.get_optimal_assignments(ignore_elite=True)
                upgrades = optimizer.calculate_upgrade_requirements(curr, pot)

                st.session_state.suggestions = upgrades
                st.session_state.analysis_done = True
                status.update(label="✅ 分析完成", state="complete", expanded=False)

                # 分析完成后刷新显示
                st.rerun()

            except Exception as e:
                status.update(label="❌ 分析出错", state="error")
                st.error(f"算法错误: {str(e)}")
                st.stop()

    # 2. 如果已有结果，优先展示下载区 (放在顶部更方便)
    if st.session_state.get('final_result_ready', False):
        st.markdown("### 🎉 排班表已生成")
        result_container = st.container(border=True)
        with result_container:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.metric("预计最终效率", f"{st.session_state.final_eff:.2f}")
            with c2:
                st.download_button(
                    label="📥 下载 MAA 排班 JSON",
                    data=st.session_state.final_result_json,
                    file_name="maa_schedule_optimized.json",
                    mime="application/json",
                    type="primary",
                    use_container_width=True
                )
            st.caption("注：此文件包含您刚才勾选并应用的练度修改。")

    # ==========================================
    # 优化后的：3. 练度建议交互区
    # ==========================================
    st.markdown("### 🛠️ 练度优化建议")


    # --- 辅助函数：获取头像 URL ---
    def get_avatar_url(char_id):
        # 使用 Aceship 的 GitHub 资源库，需要标准 char_id (如 char_102_texas)
        # 如果你的 id 是纯数字或其他格式，这里可能需要调整，或者使用 prts.wiki
        return f"https://raw.githubusercontent.com/Aceship/Arknight-Images/main/avatars/{char_id}.png"


    # --- 辅助函数：数据去重与排序 ---
    def process_suggestions(suggestions):
        seen = set()
        unique_list = []
        # 按效率提升降序排列
        sorted_sugg = sorted(suggestions, key=lambda x: x['gain'], reverse=True)

        for item in sorted_sugg:
            # 生成一个唯一标识符用于去重
            if item.get('type') == 'bundle':
                # 对于组合，使用所有干员ID的组合作为唯一键
                uid = "bundle_" + "_".join(sorted([str(o['id']) for o in item['ops']]))
            else:
                uid = f"single_{item['id']}"

            if uid not in seen:
                seen.add(uid)
                unique_list.append(item)
        return unique_list


    # 处理数据
    if not st.session_state.suggestions:
        st.info("✨ 当前练度已满足该配置的理论最优解，无需额外提升。")
        processed_suggestions = []
    else:
        processed_suggestions = process_suggestions(st.session_state.suggestions)
        st.write(f"检测到 **{len(processed_suggestions)}** 项可提升效率的优化点：")

    # --- 样式优化 ---
    st.markdown("""
    <style>
    .op-card {
        background-color: #262730; /* 适配暗色模式，如果是亮色模式需改为 #f0f2f6 */
        border: 1px solid #464b59;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .eff-badge {
        background-color: rgba(255, 75, 75, 0.2);
        color: #ff4b4b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9em;
        white-space: nowrap;
    }
    .eff-badge-high {
        background-color: rgba(255, 215, 0, 0.2);
        color: #ffd700;
    }
    .op-name {
        font-weight: bold;
        font-size: 1.1em;
        margin-left: 10px;
    }
    .op-desc {
        font-size: 0.85em;
        color: #a0a0a0;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 表单区域 ---
    with st.form("upgrade_form"):
        # 全选控制逻辑
        # 使用 session_state 来控制全选状态稍微复杂，这里用简单的列头Checkbox作为全选不太容易实现联动
        # 替代方案：默认全部勾选，或者提供两个按钮在表单外控制（Streamlit限制）
        # 这里采用：顶部加一个说明，默认不勾选，或者用户手动勾选。
        # 为了体验，通常建议**默认全选**或提供**全选按钮**。
        # 由于Streamlit Form机制，我们在Form内部很难做动态的全选/反选交互。
        # 折中方案：默认全部 False，用户自己勾。

        # Grid 布局
        cols = st.columns(1)  # 手机端友好，单列布局

        selected_indices_in_processed = []

        # 遍历渲染列表
        for idx, item in enumerate(processed_suggestions):
            # 获取数据
            gain_val = item['gain']
            is_bundle = item.get('type') == 'bundle'

            # 准备显示的 HTML 内容
            if is_bundle:
                # 组合建议
                ops_info = item['ops']
                # 获取头像 (仅展示前2个，避免过多)
                avatars_html = ""
                names_text = []
                details_text = []
                ids_for_key = []

                for o in ops_info:
                    url = get_avatar_url(o.get('id'))
                    avatars_html += f'<img src="{url}" style="width: 40px; height: 40px; border-radius: 4px; margin-right: 5px;">'
                    names_text.append(o['name'])
                    details_text.append(f"{o['name']}: 精{o['current']}→{o['target']}")
                    ids_for_key.append(str(o.get('id')))

                display_name = " + ".join(names_text)
                desc_text = " | ".join(details_text)
                key_suffix = "_".join(ids_for_key)
            else:
                # 单人建议
                url = get_avatar_url(item.get('id'))
                avatars_html = f'<img src="{url}" style="width: 45px; height: 45px; border-radius: 4px;">'
                display_name = item['name']
                desc_text = f"当前: 精{item['current']}  ➜  目标: 精{item['target']}"
                key_suffix = str(item.get('id'))

            # 效率颜色区分：超过 20% 显示金色，否则红色
            badge_class = "eff-badge eff-badge-high" if gain_val >= 20 else "eff-badge"

            # 使用 container 模拟卡片
            # 注意：在 Form 里无法使用复杂的嵌套 columns 布局而不破坏 checkbox 对齐
            # 这里的方案是：Checkbox 在左，右侧使用 HTML 渲染详情

            c1, c2 = st.columns([0.1, 0.9])
            with c1:
                # 垂直居中稍微难一点，这里简单处理
                st.write("")
                st.write("")
                # 唯一的 Key，结合版本号防止状态混淆
                unique_key = f"chk_{st.session_state.list_version}_{idx}_{key_suffix}"
                is_checked = st.checkbox("选择", key=unique_key, label_visibility="collapsed")
                if is_checked:
                    selected_indices_in_processed.append(idx)

            with c2:
                st.markdown(f"""
                <div class="op-card">
                    <div style="display:flex; align-items:center; flex-grow:1;">
                        {avatars_html}
                        <div style="display:flex; flex-direction:column;">
                            <span class="op-name">{display_name}</span>
                            <span class="op-desc">{desc_text}</span>
                        </div>
                    </div>
                    <div class="{badge_class}">
                        +{gain_val:.2f}% 效率
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # 操作按钮
        c_btn1, c_btn2 = st.columns([3, 1])
        with c_btn1:
            submit_btn = st.form_submit_button("🚀 应用选中修改并生成排班", type="primary", use_container_width=True)
        with c_btn2:
            st.caption(f"已选中: {len(selected_indices_in_processed)} 项")

    # ==========================================
    # 4. 处理生成逻辑 (适配新的去重列表)
    # ==========================================
    if submit_btn:
        with st.spinner("正在写入数据并重新演算..."):
            # A. 复制当前数据
            new_ops_data = copy.deepcopy(st.session_state.user_ops)
            modified_names = []

            # B. 应用勾选的修改 (注意：这里要用 processed_suggestions)
            for idx in selected_indices_in_processed:
                item = processed_suggestions[idx]  # <--- 使用去重后的列表

                if item.get('type') == 'bundle':
                    for o in item['ops']:
                        suc, name = upgrade_operator_in_memory(new_ops_data, o.get('id'), o.get('name'),
                                                               o['target'])
                        if suc: modified_names.append(name)
                else:
                    suc, name = upgrade_operator_in_memory(new_ops_data, item.get('id'), item.get('name'),
                                                           item['target'])
                    if suc: modified_names.append(name)

            # ... (后续代码保持不变，直到 st.rerun()) ...

            # --- 以下代码直接接你原有的 C, D, E 步骤 ---
            # C. 保存到硬盘
            if modified_names:
                save_success = save_user_data(st.session_state.user_hash, new_ops_data)
                if not save_success:
                    st.error("保存数据失败，请联系管理员")
                    st.stop()
                st.session_state.user_ops = new_ops_data

            # D. 生成最终排班
            run_ops_path = f"run_ops_{st.session_state.user_hash}.json"
            run_conf_path = f"run_conf_{st.session_state.user_hash}.json"

            try:
                with open(run_ops_path, "w", encoding='utf-8') as f:
                    json.dump(new_ops_data, f, ensure_ascii=False)
                with open(run_conf_path, "w", encoding='utf-8') as f:
                    json.dump(st.session_state.user_conf, f, ensure_ascii=False)

                optimizer = WorkplaceOptimizer("internal", run_ops_path, run_conf_path)
                final_res = optimizer.get_optimal_assignments(ignore_elite=False)

                raw_res = final_res.get('raw_results', [])
                st.session_state.final_eff = raw_res[0].total_efficiency if raw_res else 0
                st.session_state.final_result_json = json.dumps(clean_data(final_res), ensure_ascii=False, indent=2)

                st.session_state.final_result_ready = True
                st.session_state.analysis_done = False
                st.session_state.suggestions = []

                if modified_names:
                    st.session_state.list_version += 1

                if modified_names:
                    st.toast(f"✅ 已更新 {len(modified_names)} 位干员练度！", icon="💾")
                else:
                    st.toast("✅ 排班生成成功！", icon="📄")

                time.sleep(0.5)
                st.rerun()

            except Exception as e:
                st.error(f"计算发生错误: {e}")
            finally:
                if os.path.exists(run_ops_path): os.remove(run_ops_path)
                if os.path.exists(run_conf_path): os.remove(run_conf_path)