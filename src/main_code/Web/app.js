// ==================== 全局变量 ====================
const tabs = document.querySelectorAll(".tab");
const tabContents = document.querySelectorAll(".tab-content");
const logContainer = document.getElementById("logContainer");
const conditionsContainer = document.getElementById("conditionsContainer");
const conditionTypeList = document.getElementById("conditionTypeList");

// 条件类型示例（可替换为你的配置）
const conditionTypes = [
    { id: 1, name: "市盈率 PE" },
    { id: 2, name: "市净率 PB" },
    { id: 3, name: "成交量" },
    { id: 4, name: "换手率" }
];

// 当前选中条件
let currentConditions = [];

// ==================== 页签切换 ====================

document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetId = tab.dataset.tab;

            // 切按钮状态
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            // 切内容
            tabContents.forEach(tc => {
                tc.classList.toggle("active", tc.id === targetId);
            });
        });
    });
});

// ==================== 日志功能 ====================
function addLog(message, type = "info") {
    const entry = document.createElement("div");
    entry.classList.add("log-entry", `log-${type}`);
    entry.textContent = `[${type.toUpperCase()}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 清空日志
document.getElementById("clearLogBtn").addEventListener("click", () => {
    logContainer.innerHTML = "";
    addLog("日志已清空", "info");
});

// ==================== 条件操作 ====================

// 打开添加条件模态框
document.getElementById("addConditionBtn").addEventListener("click", () => {
    conditionTypeList.innerHTML = "";
    conditionTypes.forEach(ct => {
        const btn = document.createElement("button");
        btn.classList.add("btn", "btn-secondary");
        btn.style.width = "100%";
        btn.style.marginBottom = "6px";
        btn.textContent = ct.name;
        btn.addEventListener("click", () => addCondition(ct));
        conditionTypeList.appendChild(btn);
    });
    document.getElementById("addConditionModal").classList.add("active");
});

// 关闭条件模态框
document.getElementById("closeModalBtn").addEventListener("click", () => {
    document.getElementById("addConditionModal").classList.remove("active");
});

// 添加条件卡片
function addCondition(type) {
    document.getElementById("addConditionModal").classList.remove("active");

    const card = document.createElement("div");
    card.classList.add("condition-card");
    
    card.innerHTML = `
        <div class="condition-header">
            <span class="condition-name">${type.name}</span>
            <div class="condition-actions">
                <button class="icon-btn remove-btn" title="删除">✖️</button>
            </div>
        </div>
        <div class="condition-row">
            <label>影响因子 (0-1000)</label>
            <input type="number" class="factor-input" min="0" max="1000" value="100">
        </div>
        <div class="condition-row">
            <label>条件操作</label>
            <select class="condition-value">
                <option value=">">大于</option>
                <option value="<">小于</option>
            </select>
            <input type="number" class="condition-threshold" placeholder="阈值">
        </div>
        <div class="condition-operator">
            <button class="operator-btn active">AND</button>
            <button class="operator-btn">OR</button>
        </div>
        <div class="sub-condition"></div>
    `;

    // 删除按钮
    card.querySelector(".remove-btn").addEventListener("click", () => {
        conditionsContainer.removeChild(card);
        addLog(`已删除条件: ${type.name}`, "warning");
    });

    conditionsContainer.appendChild(card);
    addLog(`已添加条件: ${type.name}`, "success");
}

// ==================== 股票操作 ====================

// 打开添加股票模态框
document.getElementById("addStockBtn").addEventListener("click", () => {
    document.getElementById("addStockModal").classList.add("active");
});

// 关闭股票模态框
document.getElementById("closeStockModalBtn").addEventListener("click", () => {
    document.getElementById("addStockModal").classList.remove("active");
});

// 确认添加股票
document.getElementById("confirmAddStockBtn").addEventListener("click", () => {
    const code = document.getElementById("stockCodeInput").value;
    const price = document.getElementById("buyPriceInput").value;
    const date = document.getElementById("buyDateInput").value;

    if(!code || !price || !date) {
        alert("请填写完整股票信息！");
        return;
    }

    const tbody = document.getElementById("holdingsTableBody");
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td class="stock-code">${code}</td>
        <td>待填写</td>
        <td>${price}</td>
        <td>${date}</td>
        <td>-</td>
        <td>-</td>
        <td>
            <button class="icon-btn remove-btn">✖️</button>
        </td>
    `;

    tr.querySelector(".remove-btn").addEventListener("click", () => {
        tbody.removeChild(tr);
        addLog(`已删除持仓股票: ${code}`, "warning");
    });

    tbody.appendChild(tr);
    addLog(`已添加持仓股票: ${code}`, "success");

    document.getElementById("addStockModal").classList.remove("active");
    // 清空输入
    document.getElementById("stockCodeInput").value = "";
    document.getElementById("buyPriceInput").value = "";
    document.getElementById("buyDateInput").value = "";
});

// ==================== 按钮接口占位 ====================

// 更新数据
document.getElementById("updateDataBtn").addEventListener("click", () => {
    console.log("哇哈哈哈哈哈哈哈")
    addLog("触发更新数据接口", "info");
    // TODO: 调用后端接口更新数据
});

// 关闭后台
document.getElementById("stopBackendBtn").addEventListener("click", () => {
    addLog("触发关闭后台接口", "warning");
    // TODO: 调用后端接口关闭后台服务
});

// 开始选股
document.getElementById("startSelectionBtn").addEventListener("click", () => {
    console.
    addLog("触发开始选股接口", "info");
    // TODO: 调用后端接口执行选股
});

// 设置买入条件
document.getElementById("setBuyConditionsBtn").addEventListener("click", () => {
    addLog("打开买入条件配置", "info");
    // TODO: 打开买入条件配置界面或模态框
});

// 设置卖出条件
document.getElementById("setSellConditionsBtn").addEventListener("click", () => {
    addLog("打开卖出条件配置", "info");
    // TODO: 打开卖出条件配置界面或模态框
});

// 运行回测
document.getElementById("runBacktestBtn").addEventListener("click", () => {
    addLog("触发回测接口", "info");
    // TODO: 调用后端接口执行回测
});

// 分析当前选股
document.getElementById("analyzeHoldingsBtn").addEventListener("click", () => {
    addLog("触发分析当前选股接口", "info");
    // TODO: 调用后端接口分析当前持仓
});

// 导出配置
document.getElementById("exportConfigBtn").addEventListener("click", () => {
    addLog("触发导出条件配置接口", "info");
    // TODO: 导出当前条件配置到本地文件
});

// 导入配置
document.getElementById("importConfigBtn").addEventListener("click", () => {
    addLog("触发导入条件配置接口", "info");
    // TODO: 弹窗选择本地配置文件并加载
});
