// Minimal pybind11 bindings for validating the vendor API lifecycle on Linux.
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>

#include "DstarTradeApi.h"
#include "field_converters.h"
#include "trade_spi_adapter.h"

namespace py = pybind11;

namespace {

// Use the vendor release function for every successfully created API instance.
struct DstarApiDeleter {
    void operator()(IDstarTradeApi* api) const noexcept {
        if (api != nullptr) {
            FreeDstarTradeApi(api);
        }
    }
};

// The unique pointer guarantees release if version conversion raises an exception.
using DstarApiHandle = std::unique_ptr<IDstarTradeApi, DstarApiDeleter>;

// 从 Python dict 中读取必填字段；缺失字段直接给出结构体名和字段名。
py::handle require_field(const py::dict& data, const char* struct_name, const char* field_name) {
    py::str key(field_name);
    if (!data.contains(key)) {
        throw py::value_error(
            std::string("Missing required field for ") + struct_name + ": " + field_name
        );
    }
    return data[key];
}

// 将 Python 字符串安全写入官方固定长度 char 数组；保留 NUL 结尾。
template <std::size_t Size>
void set_string_field(
    char (&destination)[Size],
    const py::dict& data,
    const char* struct_name,
    const char* field_name
) {
    static_assert(Size > 0, "Dstar character arrays must have positive capacity");
    std::string value = py::cast<std::string>(require_field(data, struct_name, field_name));
    if (value.size() >= Size) {
        throw py::value_error(
            std::string("Field ") + struct_name + "." + field_name +
            " exceeds fixed char array capacity"
        );
    }
    std::memset(destination, 0, Size);
    std::memcpy(destination, value.data(), value.size());
}

// 将 Python 数值字段转换为官方 C++ 标量类型。
template <typename Target>
void set_number_field(
    Target& destination,
    const py::dict& data,
    const char* struct_name,
    const char* field_name
) {
    destination = py::cast<Target>(require_field(data, struct_name, field_name));
}

// 兼容官方 char 枚举字段：Python 层先以 int 表示，写回 C++ char。
void set_char_code_field(
    char& destination,
    const py::dict& data,
    const char* struct_name,
    const char* field_name
) {
    destination = static_cast<char>(py::cast<int>(require_field(data, struct_name, field_name)));
}

// 将 UTF-8 bytes 按 replace 策略解码为 Python 字符串。
py::str decode_utf8_replace(const char* value, int length) {
    if (length < 0) {
        length = 0;
    }
    PyObject* decoded = PyUnicode_DecodeUTF8(value, static_cast<Py_ssize_t>(length), "replace");
    if (decoded == nullptr) {
        throw py::error_already_set();
    }
    return py::reinterpret_steal<py::str>(decoded);
}

// 以下函数把 Python dict 严格转换为对应 C++ 请求/配置结构体。
DstarApiReqLoginField make_req_login_field(const py::dict& data) {
    DstarApiReqLoginField field{};
    set_string_field(field.AccountNo, data, "DstarApiReqLoginField", "AccountNo");
    set_string_field(field.Password, data, "DstarApiReqLoginField", "Password");
    set_string_field(field.AppId, data, "DstarApiReqLoginField", "AppId");
    set_string_field(field.LicenseNo, data, "DstarApiReqLoginField", "LicenseNo");
    return field;
}

DstarApiSubmitInfoField make_submit_info_field(const py::dict& data) {
    DstarApiSubmitInfoField field{};
    set_string_field(field.AccountNo, data, "DstarApiSubmitInfoField", "AccountNo");
    set_char_code_field(field.AuthType, data, "DstarApiSubmitInfoField", "AuthType");
    set_number_field(field.AuthKeyVersion, data, "DstarApiSubmitInfoField", "AuthKeyVersion");
    set_string_field(field.SystemInfo, data, "DstarApiSubmitInfoField", "SystemInfo");
    set_string_field(field.ClientLoginIp, data, "DstarApiSubmitInfoField", "ClientLoginIp");
    set_number_field(field.ClientLoginPort, data, "DstarApiSubmitInfoField", "ClientLoginPort");
    set_string_field(
        field.ClientLoginDateTime, data, "DstarApiSubmitInfoField", "ClientLoginDateTime"
    );
    set_string_field(field.ClientAppId, data, "DstarApiSubmitInfoField", "ClientAppId");
    set_string_field(field.LicenseNo, data, "DstarApiSubmitInfoField", "LicenseNo");
    return field;
}

DstarApiInitQryInfoField make_init_qry_info_field(const py::dict& data) {
    DstarApiInitQryInfoField field{};
    set_number_field(field.ContractInitQryFlag, data, "DstarApiInitQryInfoField", "ContractInitQryFlag");
    set_number_field(field.CmbContractInitQryFlag, data, "DstarApiInitQryInfoField", "CmbContractInitQryFlag");
    set_number_field(field.SeatInitQryFlag, data, "DstarApiInitQryInfoField", "SeatInitQryFlag");
    set_number_field(field.TrdFeeInitQryFlag, data, "DstarApiInitQryInfoField", "TrdFeeInitQryFlag");
    set_number_field(field.TrdMarInitQryFlag, data, "DstarApiInitQryInfoField", "TrdMarInitQryFlag");
    set_number_field(field.TrdRightInitQryFlag, data, "DstarApiInitQryInfoField", "TrdRightInitQryFlag");
    set_number_field(field.AccountCommListInitQryFlag, data, "DstarApiInitQryInfoField", "AccountCommListInitQryFlag");
    set_number_field(field.TrdExchangeStateInitQryFlag, data, "DstarApiInitQryInfoField", "TrdExchangeStateInitQryFlag");
    set_number_field(field.PrePositionInitQryFlag, data, "DstarApiInitQryInfoField", "PrePositionInitQryFlag");
    set_number_field(field.OrderInitQryFlag, data, "DstarApiInitQryInfoField", "OrderInitQryFlag");
    set_number_field(field.OfferInitQryFlag, data, "DstarApiInitQryInfoField", "OfferInitQryFlag");
    set_number_field(field.MatchInitQryFlag, data, "DstarApiInitQryInfoField", "MatchInitQryFlag");
    set_number_field(field.CashInOutInitQryFlag, data, "DstarApiInitQryInfoField", "CashInOutInitQryFlag");
    return field;
}

DstarApiReqPwdModField make_req_pwd_mod_field(const py::dict& data) {
    DstarApiReqPwdModField field{};
    set_string_field(field.Passwd, data, "DstarApiReqPwdModField", "Passwd");
    set_string_field(field.OldPasswd, data, "DstarApiReqPwdModField", "OldPasswd");
    return field;
}

DstarApiReqOrderInsertField make_req_order_insert_field(const py::dict& data) {
    DstarApiReqOrderInsertField field{};
    set_char_code_field(field.Direct, data, "DstarApiReqOrderInsertField", "Direct");
    set_char_code_field(field.Offset, data, "DstarApiReqOrderInsertField", "Offset");
    set_char_code_field(field.Hedge, data, "DstarApiReqOrderInsertField", "Hedge");
    set_char_code_field(field.OrderType, data, "DstarApiReqOrderInsertField", "OrderType");
    set_char_code_field(field.ValidType, data, "DstarApiReqOrderInsertField", "ValidType");
    set_number_field(field.SeatIndex, data, "DstarApiReqOrderInsertField", "SeatIndex");
    set_number_field(field.AccountIndex, data, "DstarApiReqOrderInsertField", "AccountIndex");
    set_number_field(field.ContractIndex, data, "DstarApiReqOrderInsertField", "ContractIndex");
    set_string_field(field.ContractNo, data, "DstarApiReqOrderInsertField", "ContractNo");
    set_number_field(field.OrderQty, data, "DstarApiReqOrderInsertField", "OrderQty");
    set_number_field(field.MinQty, data, "DstarApiReqOrderInsertField", "MinQty");
    set_number_field(field.OrderPrice, data, "DstarApiReqOrderInsertField", "OrderPrice");
    set_number_field(field.ClientReqId, data, "DstarApiReqOrderInsertField", "ClientReqId");
    set_number_field(field.Reference, data, "DstarApiReqOrderInsertField", "Reference");
    set_number_field(field.UdpAuthCode, data, "DstarApiReqOrderInsertField", "UdpAuthCode");
    return field;
}

DstarApiReqOfferInsertField make_req_offer_insert_field(const py::dict& data) {
    DstarApiReqOfferInsertField field{};
    set_char_code_field(field.BuyOffset, data, "DstarApiReqOfferInsertField", "BuyOffset");
    set_char_code_field(field.SellOffset, data, "DstarApiReqOfferInsertField", "SellOffset");
    set_number_field(field.AccountIndex, data, "DstarApiReqOfferInsertField", "AccountIndex");
    set_number_field(field.ClientReqId, data, "DstarApiReqOfferInsertField", "ClientReqId");
    set_number_field(field.ContractIndex, data, "DstarApiReqOfferInsertField", "ContractIndex");
    set_string_field(field.ContractNo, data, "DstarApiReqOfferInsertField", "ContractNo");
    set_number_field(field.OrderQty, data, "DstarApiReqOfferInsertField", "OrderQty");
    set_number_field(field.BuyPrice, data, "DstarApiReqOfferInsertField", "BuyPrice");
    set_number_field(field.SellPrice, data, "DstarApiReqOfferInsertField", "SellPrice");
    set_number_field(field.SeatIndex, data, "DstarApiReqOfferInsertField", "SeatIndex");
    set_string_field(field.EnquiryNo, data, "DstarApiReqOfferInsertField", "EnquiryNo");
    set_number_field(field.Reference, data, "DstarApiReqOfferInsertField", "Reference");
    set_number_field(field.UdpAuthCode, data, "DstarApiReqOfferInsertField", "UdpAuthCode");
    return field;
}

DstarApiReqOfferInsertNewField make_req_offer_insert_new_field(const py::dict& data) {
    DstarApiReqOfferInsertNewField field{};
    set_char_code_field(field.BuyOffset, data, "DstarApiReqOfferInsertNewField", "BuyOffset");
    set_char_code_field(field.SellOffset, data, "DstarApiReqOfferInsertNewField", "SellOffset");
    set_number_field(field.AccountIndex, data, "DstarApiReqOfferInsertNewField", "AccountIndex");
    set_number_field(field.ClientReqId, data, "DstarApiReqOfferInsertNewField", "ClientReqId");
    set_number_field(field.ContractIndex, data, "DstarApiReqOfferInsertNewField", "ContractIndex");
    set_string_field(field.ContractNo, data, "DstarApiReqOfferInsertNewField", "ContractNo");
    set_number_field(field.BuyOrderQty, data, "DstarApiReqOfferInsertNewField", "BuyOrderQty");
    set_number_field(field.SellOrderQty, data, "DstarApiReqOfferInsertNewField", "SellOrderQty");
    set_number_field(field.BuyPrice, data, "DstarApiReqOfferInsertNewField", "BuyPrice");
    set_number_field(field.SellPrice, data, "DstarApiReqOfferInsertNewField", "SellPrice");
    set_number_field(field.SeatIndex, data, "DstarApiReqOfferInsertNewField", "SeatIndex");
    set_string_field(field.EnquiryNo, data, "DstarApiReqOfferInsertNewField", "EnquiryNo");
    set_number_field(field.Reference, data, "DstarApiReqOfferInsertNewField", "Reference");
    set_number_field(field.UdpAuthCode, data, "DstarApiReqOfferInsertNewField", "UdpAuthCode");
    set_number_field(field.ReplaceId, data, "DstarApiReqOfferInsertNewField", "ReplaceId");
    return field;
}

DstarApiReqOrderDeleteField make_req_order_delete_field(const py::dict& data) {
    DstarApiReqOrderDeleteField field{};
    set_number_field(field.AccountIndex, data, "DstarApiReqOrderDeleteField", "AccountIndex");
    set_number_field(field.ClientReqId, data, "DstarApiReqOrderDeleteField", "ClientReqId");
    set_number_field(field.UdpAuthCode, data, "DstarApiReqOrderDeleteField", "UdpAuthCode");
    set_number_field(field.Reference, data, "DstarApiReqOrderDeleteField", "Reference");
    set_number_field(field.SeatIndex, data, "DstarApiReqOrderDeleteField", "SeatIndex");
    set_number_field(field.OrderId, data, "DstarApiReqOrderDeleteField", "OrderId");
    set_string_field(field.SystemNo, data, "DstarApiReqOrderDeleteField", "SystemNo");
    return field;
}

DstarApiReqCmbOrderInsertField make_req_cmb_order_insert_field(const py::dict& data) {
    DstarApiReqCmbOrderInsertField field{};
    set_char_code_field(field.Direct, data, "DstarApiReqCmbOrderInsertField", "Direct");
    set_char_code_field(field.Offset, data, "DstarApiReqCmbOrderInsertField", "Offset");
    set_char_code_field(field.Hedge, data, "DstarApiReqCmbOrderInsertField", "Hedge");
    set_char_code_field(field.OrderType, data, "DstarApiReqCmbOrderInsertField", "OrderType");
    set_char_code_field(field.ValidType, data, "DstarApiReqCmbOrderInsertField", "ValidType");
    set_number_field(field.SeatIndex, data, "DstarApiReqCmbOrderInsertField", "SeatIndex");
    set_number_field(field.AccountIndex, data, "DstarApiReqCmbOrderInsertField", "AccountIndex");
    set_number_field(field.ContractIndex1, data, "DstarApiReqCmbOrderInsertField", "ContractIndex1");
    set_string_field(field.ContractNo1, data, "DstarApiReqCmbOrderInsertField", "ContractNo1");
    set_number_field(field.ContractIndex2, data, "DstarApiReqCmbOrderInsertField", "ContractIndex2");
    set_string_field(field.ContractNo2, data, "DstarApiReqCmbOrderInsertField", "ContractNo2");
    set_number_field(field.OrderQty, data, "DstarApiReqCmbOrderInsertField", "OrderQty");
    set_number_field(field.MinQty, data, "DstarApiReqCmbOrderInsertField", "MinQty");
    set_number_field(field.OrderPrice, data, "DstarApiReqCmbOrderInsertField", "OrderPrice");
    set_number_field(field.ClientReqId, data, "DstarApiReqCmbOrderInsertField", "ClientReqId");
    set_number_field(field.Reference, data, "DstarApiReqCmbOrderInsertField", "Reference");
    set_number_field(field.UdpAuthCode, data, "DstarApiReqCmbOrderInsertField", "UdpAuthCode");
    return field;
}

class NativeTradeApi {
public:
    // 构造时创建官方 API 实例；失败时立刻抛出异常。
    NativeTradeApi() : api_(CreateDstarTradeApi()) {
        if (api_ == nullptr) {
            throw std::runtime_error("CreateDstarTradeApi() returned null");
        }
    }

    // 析构时释放官方 API；Python 不管理 IDstarTradeApi* 生命周期。
    ~NativeTradeApi() {
        if (api_ != nullptr) {
            FreeDstarTradeApi(api_);
            api_ = nullptr;
        }
    }

    NativeTradeApi(const NativeTradeApi&) = delete;
    NativeTradeApi& operator=(const NativeTradeApi&) = delete;
    NativeTradeApi(NativeTradeApi&&) = delete;
    NativeTradeApi& operator=(NativeTradeApi&&) = delete;

    // 注册 Python dispatcher，并将 C++ SPI 适配器交给官方 API。
    void register_callback(py::object dispatcher) {
        if (!py::hasattr(dispatcher, "on_event")) {
            throw py::value_error("dispatcher must provide on_event(event_name, payload)");
        }
        auto new_spi = std::make_unique<dstar_trade_py::PyTradeSpiAdapter>(dispatcher);
        api_->RegisterSpi(new_spi.get());
        spi_ = std::move(new_spi);
    }

    // 注册前置地址。
    void register_front_address(const std::string& ip, int port) {
        if (ip.size() >= sizeof(front_ip_)) {
            throw py::value_error("ip exceeds DstarApiIpType capacity");
        }
        std::memset(front_ip_, 0, sizeof(front_ip_));
        std::memcpy(front_ip_, ip.data(), ip.size());
        api_->RegisterFrontAddress(front_ip_, static_cast<DstarApiPortType>(port));
    }

    // 设置 API 日志路径。
    void set_api_log_path(const std::string& path) {
        if (path.size() >= sizeof(api_log_path_)) {
            throw py::value_error("path exceeds DstarApiPathType capacity");
        }
        std::memset(api_log_path_, 0, sizeof(api_log_path_));
        std::memcpy(api_log_path_, path.data(), path.size());
        api_->SetApiLogPath(api_log_path_);
    }

    // 设置并保存登录信息，避免官方 API 延迟读取时指针悬空。
    void set_login_info(const py::dict& login_info) {
        login_info_ = make_req_login_field(login_info);
        api_->SetLoginInfo(&login_info_);
    }

    // 设置 CPU 绑定参数。
    void set_cpu_id(int recv_notice_cpu_id, int log_cpu_id) {
        api_->SetCpuId(recv_notice_cpu_id, log_cpu_id);
    }

    // 设置通知流订阅起点。
    void set_subscribe_start_id(long long start_id) {
        api_->SetSubscribeStartId(start_id);
    }

    // 设置实时数据过滤模式。
    void set_real_time_data_filter(int filter) {
        api_->SetRealTimeDataFilter(filter);
    }

    // 设置运行模式。
    void set_run_mode(int mode) {
        api_->SetRunMode(mode);
    }

    // 获取系统采集信息，并返回 ret、长度、密钥版本和字符串数据。
    py::dict get_system_info() {
        char system_info[1024] = {};
        int length = static_cast<int>(sizeof(system_info));
        unsigned int auth_key_version = 0;
        int ret = api_->GetSystemInfo(system_info, &length, &auth_key_version);
        int decode_length = length;
        if (decode_length > static_cast<int>(sizeof(system_info))) {
            decode_length = static_cast<int>(sizeof(system_info));
        }

        py::dict result;
        result["return_code"] = ret;
        result["length"] = length;
        result["auth_key_version"] = auth_key_version;
        result["system_info"] = decode_utf8_replace(system_info, decode_length);
        return result;
    }

    // 设置并保存上报信息。
    void set_submit_info(const py::dict& submit_info) {
        submit_info_ = make_submit_info_field(submit_info);
        api_->SetSubmitInfo(&submit_info_);
    }

    // 设置并保存初始化查询信息。
    void set_init_qry_info(const py::dict& init_qry_info) {
        init_qry_info_ = make_init_qry_info_field(init_qry_info);
        api_->SetInitQryInfo(&init_qry_info_);
    }

    // 初始化官方 API；仅返回官方同步返回值。
    int init() {
        return api_->Init();
    }

    // 请求最新客户请求号。
    int req_last_client_req_id() {
        return api_->ReqLastClientReqId();
    }

    // 请求修改密码。
    int req_pwd_mod(const py::dict& data) {
        DstarApiReqPwdModField field = make_req_pwd_mod_field(data);
        return api_->ReqPwdMod(&field);
    }

    // 请求普通报单。
    int req_order_insert(const py::dict& data) {
        DstarApiReqOrderInsertField field = make_req_order_insert_field(data);
        return api_->ReqOrderInsert(&field);
    }

    // 请求报价。
    int req_offer_insert(const py::dict& data) {
        DstarApiReqOfferInsertField field = make_req_offer_insert_field(data);
        return api_->ReqOfferInsert(&field);
    }

    // 请求新报价。
    int req_offer_insert_new(const py::dict& data) {
        DstarApiReqOfferInsertNewField field = make_req_offer_insert_new_field(data);
        return api_->ReqOfferInsertNew(&field);
    }

    // 请求撤单。
    int req_order_delete(const py::dict& data) {
        DstarApiReqOrderDeleteField field = make_req_order_delete_field(data);
        return api_->ReqOrderDelete(&field);
    }

    // 请求组合报单。
    int req_cmb_order_insert(const py::dict& data) {
        DstarApiReqCmbOrderInsertField field = make_req_cmb_order_insert_field(data);
        return api_->ReqCmbOrderInsert(&field);
    }

    // 请求资金查询。
    int req_qry_fund() {
        return api_->ReqQryFund();
    }

    // 请求持仓查询。
    int req_qry_position() {
        return api_->ReqQryPosition();
    }

    // 读取官方 API 版本号。
    std::string get_api_version() {
        const char* version = api_->GetApiVersion();
        if (version == nullptr) {
            return "";
        }
        return std::string(version);
    }

private:
    IDstarTradeApi* api_ = nullptr;
    std::unique_ptr<dstar_trade_py::PyTradeSpiAdapter> spi_;
    DstarApiIpType front_ip_{};
    DstarApiPathType api_log_path_{};
    DstarApiReqLoginField login_info_{};
    DstarApiSubmitInfoField submit_info_{};
    DstarApiInitQryInfoField init_qry_info_{};
};

// Create a temporary API instance, read its version, and release it before returning.
std::string get_api_version() {
    DstarApiHandle api(CreateDstarTradeApi());
    if (!api) {
        throw std::runtime_error(
            "CreateDstarTradeApi() returned null; verify the Linux vendor library and runtime environment"
        );
    }

    const char* version = api->GetApiVersion();
    if (version == nullptr || version[0] == '\0') {
        throw std::runtime_error("Dstar Trade API returned an empty version string");
    }

    return std::string(version);
}

// Exercise only the vendor factory and release functions without connecting to a server.
bool create_and_free_api() {
    DstarApiHandle api(CreateDstarTradeApi());
    return static_cast<bool>(api);
}

// Copy test text into a fixed vendor char array with guaranteed termination.
template <std::size_t Size>
void copy_test_text(char (&destination)[Size], const char* source) {
    static_assert(Size > 0, "Dstar character arrays must have positive capacity");
    std::strncpy(destination, source, Size - 1);
    destination[Size - 1] = '\0';
}

// Build representative packed structures on the stack and immediately copy them.
py::dict test_field_converter_samples() {
    DstarApiRspLoginField login{};
    login.AccountIndex = 7;
    copy_test_text(login.AccountNo, "demo-account");
    copy_test_text(login.TradeDate, "20260612");
    login.UdpAuthCode = 123456;
    login.ErrorCode = DSTAR_API_ERR_SUCCESS;
    login.StartTime = 90000;
    login.StartMode = DSTAR_API_STARTMODE_TRADE;
    login.FloatFlag = DSTAR_API_YES;

    DstarApiFundField fund{};
    copy_test_text(fund.AccountNo, "demo-account");
    fund.PreEquity = 100000.5;
    fund.Equity = 100250.75;
    fund.Avail = 80000.25;
    fund.Margin = 20000.5;
    fund.PositionProfit = 250.25;

    DstarApiPositionField position{};
    copy_test_text(position.AccountNo, "demo-account");
    copy_test_text(position.ContractNo, "GC2608");
    position.PreBuyQty = 1;
    position.TodayBuyQty = 2;
    position.BuyAvgPrice = 2410.5;
    position.SerialId = 987654321ULL;

    DstarApiOrderField order{};
    order.Direct = DSTAR_API_DIRECT_BUY;
    order.Offset = DSTAR_API_OFFSET_OPEN;
    order.Hedge = DSTAR_API_HEDGE_SPECULATE;
    order.ValidType = DSTAR_API_VALID_GFD;
    order.OrderPrice = 2412.5;
    order.OrderQty = 3;
    order.OrderId = 10001;
    copy_test_text(order.AccountNo, "demo-account");
    copy_test_text(order.ContractNo1, "GC2608");
    order.OrderType = DSTAR_API_ORDERTYPE_LIMIT;
    order.OrderState = DSTAR_API_STATUS_QUEUE;

    DstarApiMatchField match{};
    copy_test_text(match.ContractNo, "GC2608");
    match.MatchQty = 2;
    match.MatchPrice = 2411.25;
    match.Offset = DSTAR_API_OFFSET_OPEN;
    match.Direct = DSTAR_API_DIRECT_BUY;
    match.Hedge = DSTAR_API_HEDGE_SPECULATE;
    match.OrderType = DSTAR_API_ORDERTYPE_LIMIT;
    match.OrderId = 10001;
    match.MatchId = 20002;
    copy_test_text(match.AccountNo, "demo-account");

    // Invalid UTF-8 is intentional and verifies the replacement decoding policy.
    DstarApiReqLoginField invalid_utf8{};
    invalid_utf8.AccountNo[0] = 'A';
    invalid_utf8.AccountNo[1] = static_cast<char>(0xFF);
    invalid_utf8.AccountNo[2] = '\0';

    // A full array without NUL verifies that conversion never reads past capacity.
    DstarApiReqLoginField unterminated{};
    std::memset(unterminated.Password, 'x', sizeof(unterminated.Password));

    py::dict samples;
    samples["login"] = dstar_trade_py::to_py_dict(&login);
    samples["fund"] = dstar_trade_py::to_py_dict(&fund);
    samples["position"] = dstar_trade_py::to_py_dict(&position);
    samples["order"] = dstar_trade_py::to_py_dict(&order);
    samples["match"] = dstar_trade_py::to_py_dict(&match);
    samples["error"] = dstar_trade_py::to_py_error_dict(DSTAR_API_ERR_NOCONNECTION);
    samples["bool"] = dstar_trade_py::to_py_bool_dict(true);
    samples["null_login"] = dstar_trade_py::to_py_dict(
        static_cast<const DstarApiRspLoginField*>(nullptr)
    );
    samples["invalid_utf8"] = dstar_trade_py::to_py_dict(&invalid_utf8);
    samples["unterminated"] = dstar_trade_py::to_py_dict(&unterminated);
    return samples;
}

// Exercise the real PyTradeSpiAdapter without connecting to a trading server.
void test_spi_dispatch(py::object dispatcher, bool raise_on_callback) {
    dstar_trade_py::PyTradeSpiAdapter adapter(dispatcher);

    DstarApiRspLoginField login{};
    login.AccountIndex = 7;
    copy_test_text(login.AccountNo, "demo-account");
    copy_test_text(login.TradeDate, "20260612");
    login.UdpAuthCode = 123456;
    login.ErrorCode = DSTAR_API_ERR_SUCCESS;

    DstarApiPositionField position{};
    copy_test_text(position.AccountNo, "demo-account");
    copy_test_text(position.ContractNo, "GC2608");
    position.TodayBuyQty = 2;
    position.SerialId = 987654321ULL;

    DstarApiOrderField order{};
    order.Direct = DSTAR_API_DIRECT_BUY;
    order.OrderState = DSTAR_API_STATUS_QUEUE;
    order.OrderId = 10001;
    copy_test_text(order.AccountNo, "demo-account");
    copy_test_text(order.ContractNo1, "GC2608");

    DstarApiFundField fund{};
    copy_test_text(fund.AccountNo, "demo-account");
    fund.Equity = 100250.75;

    adapter.OnFrontDisconnected();
    adapter.OnRspError(DSTAR_API_ERR_NOCONNECTION);
    adapter.OnRspUserLogin(&login);
    adapter.OnApiReady(998877ULL);
    adapter.OnRspQryPosition(&position, true);
    adapter.OnRtnOrder(&order);
    adapter.OnRspQryFund(&fund);

    if (raise_on_callback) {
        // The adapter must catch and log this Python exception internally.
        adapter.OnRspError(DSTAR_API_ERR_PASSWORD);
    }
}

}  // namespace

// Register the minimal native surface used by the Linux load tests.
PYBIND11_MODULE(_dstar_trade_py, module) {
    module.doc() = "Minimal Linux bindings for validating the Dstar Trade API library";
    module.attr("IS_LINUX_BUILD") = true;
    module.attr("SDK_PROTOCOL_VERSION") = DSTAR_API_PROTOCOL_VERSION;

    module.def(
        "get_api_version",
        &get_api_version,
        "Create the vendor API, return its version string, and release the instance."
    );
    module.def(
        "create_and_free_api",
        &create_and_free_api,
        "Create and immediately release a vendor API instance."
    );
    module.def(
        "_test_field_converter_samples",
        &test_field_converter_samples,
        "Return owned dictionaries produced from representative stack fields."
    );
    module.def(
        "_test_spi_dispatch",
        &test_spi_dispatch,
        py::arg("dispatcher"),
        py::arg("raise_on_callback") = false,
        "Trigger representative IDstarTradeSpi callbacks against a dispatcher."
    );

    py::class_<NativeTradeApi>(module, "NativeTradeApi")
        .def(py::init<>(), "创建并持有一个官方 IDstarTradeApi 实例。")
        .def(
            "register_callback",
            &NativeTradeApi::register_callback,
            py::arg("dispatcher"),
            "注册 Python dispatcher，dispatcher 必须提供 on_event(event_name, payload)。"
        )
        .def(
            "register_front_address",
            &NativeTradeApi::register_front_address,
            py::arg("ip"),
            py::arg("port"),
            "注册交易前置地址。"
        )
        .def(
            "set_api_log_path",
            &NativeTradeApi::set_api_log_path,
            py::arg("path"),
            "设置官方 API 日志和交易数据目录。"
        )
        .def(
            "set_login_info",
            &NativeTradeApi::set_login_info,
            py::arg("login_info"),
            "设置登录信息，入参字段对应 DstarApiReqLoginField。"
        )
        .def(
            "set_cpu_id",
            &NativeTradeApi::set_cpu_id,
            py::arg("recv_notice_cpu_id"),
            py::arg("log_cpu_id"),
            "设置接收线程和日志线程 CPU 绑定参数。"
        )
        .def(
            "set_subscribe_start_id",
            &NativeTradeApi::set_subscribe_start_id,
            py::arg("start_id"),
            "设置通知流订阅起始流号。"
        )
        .def(
            "set_real_time_data_filter",
            &NativeTradeApi::set_real_time_data_filter,
            py::arg("filter"),
            "设置实时数据过滤模式。"
        )
        .def(
            "set_run_mode",
            &NativeTradeApi::set_run_mode,
            py::arg("mode"),
            "设置官方 API 运行模式。"
        )
        .def("get_system_info", &NativeTradeApi::get_system_info, "采集并返回系统授权信息。")
        .def(
            "set_submit_info",
            &NativeTradeApi::set_submit_info,
            py::arg("submit_info"),
            "设置上报信息，入参字段对应 DstarApiSubmitInfoField。"
        )
        .def(
            "set_init_qry_info",
            &NativeTradeApi::set_init_qry_info,
            py::arg("init_qry_info"),
            "设置初始化查询信息，入参字段对应 DstarApiInitQryInfoField。"
        )
        .def("init", &NativeTradeApi::init, "初始化官方 API 并返回官方同步错误码。")
        .def(
            "req_last_client_req_id",
            &NativeTradeApi::req_last_client_req_id,
            "请求最新客户请求号。"
        )
        .def(
            "req_pwd_mod",
            &NativeTradeApi::req_pwd_mod,
            py::arg("data"),
            "提交密码修改请求，入参字段对应 DstarApiReqPwdModField。"
        )
        .def(
            "req_order_insert",
            &NativeTradeApi::req_order_insert,
            py::arg("data"),
            "提交普通报单请求，入参字段对应 DstarApiReqOrderInsertField。"
        )
        .def(
            "req_offer_insert",
            &NativeTradeApi::req_offer_insert,
            py::arg("data"),
            "提交报价请求，入参字段对应 DstarApiReqOfferInsertField。"
        )
        .def(
            "req_offer_insert_new",
            &NativeTradeApi::req_offer_insert_new,
            py::arg("data"),
            "提交新版报价请求，入参字段对应 DstarApiReqOfferInsertNewField。"
        )
        .def(
            "req_order_delete",
            &NativeTradeApi::req_order_delete,
            py::arg("data"),
            "提交撤单请求，入参字段对应 DstarApiReqOrderDeleteField。"
        )
        .def(
            "req_cmb_order_insert",
            &NativeTradeApi::req_cmb_order_insert,
            py::arg("data"),
            "提交组合报单请求，入参字段对应 DstarApiReqCmbOrderInsertField。"
        )
        .def("req_qry_fund", &NativeTradeApi::req_qry_fund, "提交资金查询请求。")
        .def("req_qry_position", &NativeTradeApi::req_qry_position, "提交持仓查询请求。")
        .def("get_api_version", &NativeTradeApi::get_api_version, "返回官方 API 版本号。");
}
