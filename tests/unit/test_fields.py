"""Tests for generated dataclasses and readable Dstar constant enums."""

from __future__ import annotations

import ast
import re
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import get_type_hints

from dstar_trade_py.enums import ENUM_BY_CPP_TYPE, Direction, Exchange
from dstar_trade_py.fields import (
    STRUCT_MODELS,
    DstarApiMatchField,
    DstarApiOfferField,
    DstarApiReqLoginField,
    DstarApiReqOrderInsertField,
    DstarApiRspOfferInsertField,
    DstarApiRspOrderDeleteField,
    DstarApiRspOrderInsertField,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_TYPE_HEADER = PROJECT_ROOT / "third_party/dstar/include/DstarTradeApiDataType.h"
STRUCT_HEADER = PROJECT_ROOT / "third_party/dstar/include/DstarTradeApiStruct.h"


def _parse_header_structs() -> dict[str, list[str]]:
    """Parse all named structures and anonymous-union fields from the header."""

    source = STRUCT_HEADER.read_text(encoding="utf-8").splitlines()
    field_pattern = re.compile(r"^\s*(?:DstarApi|DstaApi)\w+\s+(\w+)\s*;")
    result: dict[str, list[str]] = {}
    index = 0

    while index < len(source):
        match = re.match(r"^typedef struct (\w+)", source[index].strip())
        if match is None:
            index += 1
            continue

        struct_name = match.group(1)
        index += 1
        while index < len(source) and "{" not in source[index]:
            index += 1
        index += 1

        field_names: list[str] = []
        union_depth = 0
        while index < len(source):
            stripped = source[index].strip()
            if stripped.startswith("union"):
                union_depth = 1
                index += 1
                continue
            if stripped.startswith("};") and union_depth:
                union_depth = 0
                index += 1
                continue
            if stripped.startswith("}") and not union_depth:
                break

            field_match = field_pattern.match(source[index])
            if field_match is not None:
                field_names.append(field_match.group(1))
            index += 1

        result[struct_name] = field_names
        index += 1

    return result


def _parse_constant_values() -> dict[str, set[int]]:
    """Group all 90 data constants and six protocol constants by C++ type."""

    pattern = re.compile(
        r"^(?:const|static const)\s+(DstarApi\w+)\s+\w+\s*=\s*([^;]+);",
        re.MULTILINE,
    )
    result: dict[str, set[int]] = {}

    for header in (DATA_TYPE_HEADER, STRUCT_HEADER):
        source = header.read_text(encoding="utf-8")
        for cpp_type, raw_value in pattern.findall(source):
            raw_value = raw_value.strip()
            if raw_value.startswith("'"):
                value = ord(ast.literal_eval(raw_value))
            else:
                value = int(raw_value, 0)
            result.setdefault(cpp_type, set()).add(value)

    return result


def test_every_cpp_struct_has_an_exact_dataclass_mapping() -> None:
    """Every declared structure must exist with fields in original order."""

    header_structs = _parse_header_structs()

    assert len(header_structs) == 36
    for struct_name, header_fields in header_structs.items():
        model_type = STRUCT_MODELS[struct_name]
        assert is_dataclass(model_type)
        assert [field.name for field in fields(model_type)] == header_fields


def test_typedef_response_aliases_share_the_original_model() -> None:
    """The two C++ response aliases must preserve their shared binary layout."""

    assert DstarApiRspOrderDeleteField is DstarApiRspOrderInsertField
    assert DstarApiRspOfferInsertField is DstarApiRspOrderInsertField
    assert len(STRUCT_MODELS) == 38


def test_all_dataclasses_can_be_created_with_zero_defaults() -> None:
    """Every field defaults to an empty string, zero integer, or zero float."""

    for model_type in set(STRUCT_MODELS.values()):
        model = model_type()
        type_hints = get_type_hints(model_type)

        for field in fields(model):
            value = getattr(model, field.name)
            expected_type = type_hints[field.name]
            if expected_type is str:
                assert value == ""
                assert type(value) is str
            elif expected_type is float:
                assert value == 0.0
                assert type(value) is float
            else:
                assert value == 0
                assert type(value) is int


def test_dict_to_dataclass_uses_cpp_field_names() -> None:
    """Request dictionaries can be converted without renaming vendor fields."""

    payload = {
        "Direct": int(Direction.BUY),
        "Offset": ord("O"),
        "ContractNo": "GC2608",
        "OrderQty": 2,
        "OrderPrice": 2410.5,
        "ClientReqId": 42,
    }

    order = DstarApiReqOrderInsertField.from_dict(payload)

    assert order.Direct == int(Direction.BUY)
    assert order.ContractNo == "GC2608"
    assert order.OrderQty == 2
    assert order.OrderPrice == 2410.5
    assert order.ClientReqId == 42
    assert order.Hedge == 0


def test_dataclass_to_dict_returns_plain_values() -> None:
    """Models convert back to dictionaries suitable for binding conversion."""

    login = DstarApiReqLoginField(
        AccountNo="demo",
        Password="secret",
        AppId="test-app",
        LicenseNo="test-license",
    )

    assert login.to_dict() == {
        "AccountNo": "demo",
        "Password": "secret",
        "AppId": "test-app",
        "LicenseNo": "test-license",
    }


def test_anonymous_union_members_are_preserved() -> None:
    """Both names from each C++ anonymous union remain available to Python."""

    offer = DstarApiOfferField(OrderQty=3, BuyOrderQty=4)
    match = DstarApiMatchField(Premium=12.5, CloseProfit=6.25)

    assert offer.OrderQty == 3
    assert offer.BuyOrderQty == 4
    assert match.Premium == 12.5
    assert match.CloseProfit == 6.25


def test_all_header_constants_are_covered_by_readable_enums() -> None:
    """Every constant group in both headers must have a value-complete enum."""

    header_values = _parse_constant_values()

    assert sum(len(values) for values in header_values.values()) == 96
    assert set(ENUM_BY_CPP_TYPE) >= set(header_values)
    for cpp_type, values in header_values.items():
        assert {member.value for member in ENUM_BY_CPP_TYPE[cpp_type]} == values


def test_character_enums_use_integer_byte_values() -> None:
    """Single-character C++ constants are exposed as int-valued IntEnums."""

    assert Exchange.SHFE.value == ord("S")
    assert Direction.BUY.value == ord("B")
    assert isinstance(Direction.BUY.value, int)


def test_mapping_document_lists_every_structure_and_field() -> None:
    """The generated documentation must mention all structure field mappings."""

    document = (PROJECT_ROOT / "docs/field_mapping.md").read_text(encoding="utf-8")

    for struct_name, field_names in _parse_header_structs().items():
        assert f"### `{struct_name}`" in document
        for field_name in field_names:
            assert f"`{field_name}`" in document
