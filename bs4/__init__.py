"""Minimal BeautifulSoup-compatible shim used when ``beautifulsoup4`` is unavailable."""
from __future__ import annotations

import html as _html
from html import entities
from html.parser import HTMLParser
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union

NameArg = Optional[Union[str, Callable[["Tag"], bool]]]
AttrsArg = Optional[Dict[str, Any]]

VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _Node:
    __slots__ = ("name", "attrs", "children", "parent")

    def __init__(self, name: str, attrs: Iterable[tuple[str, Optional[str]]], parent: Optional["_Node"] = None) -> None:
        self.name = name
        self.attrs = {key: value or "" for key, value in attrs}
        self.children: List[Union["_Node", str]] = []
        self.parent = parent

    def append(self, child: Union["_Node", str]) -> None:
        self.children.append(child)

    def text_content(self) -> str:
        parts: List[str] = []
        for child in self.children:
            if isinstance(child, _Node):
                parts.append(child.text_content())
            else:
                parts.append(child)
        return "".join(parts)

    def render(self) -> str:
        attrs = "".join(
            f" {name}=\"{_html.escape(value, quote=True)}\"" for name, value in self.attrs.items()
        )
        if self.name in VOID_ELEMENTS:
            return f"<{self.name}{attrs}>"
        return f"<{self.name}{attrs}>{self.render_contents()}</{self.name}>"

    def render_contents(self) -> str:
        parts: List[str] = []
        for child in self.children:
            if isinstance(child, _Node):
                parts.append(child.render())
            else:
                parts.append(child)
        return "".join(parts)


class _HTMLTreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = _Node("__root__", [])
        self.current = self.root

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        node = _Node(tag, attrs, self.current)
        self.current.append(node)
        if tag.lower() not in VOID_ELEMENTS:
            self.current = node

    def handle_startendtag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        node = _Node(tag, attrs, self.current)
        self.current.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        while self.current is not self.root and self.current.name.lower() != tag:
            self.current = self.current.parent or self.root
        if self.current is not self.root:
            self.current = self.current.parent or self.root

    def handle_data(self, data: str) -> None:
        if data:
            self.current.append(data)

    def handle_entityref(self, name: str) -> None:  # pragma: no cover - uncommon
        char = chr(entities.name2codepoint.get(name, ord("?")))
        self.handle_data(char)

    def handle_charref(self, name: str) -> None:  # pragma: no cover - uncommon
        base = 16 if name.lower().startswith("x") else 10
        try:
            char = chr(int(name.lstrip("xX"), base))
        except ValueError:
            char = "?"
        self.handle_data(char)

    def handle_comment(self, data: str) -> None:  # pragma: no cover - uncommon
        self.current.append(f"<!--{data}-->")


_selector_attr_re = re.compile(
    r"\[(?P<name>[^=\]]+)(?:(?P<op>\*=|=)\s*(?P<value>\"[^\"]*\"|'[^']*'|[^\]]+))?\]"
)


@dataclass(frozen=True)
class _Selector:
    tag: Optional[str] = None
    id: Optional[str] = None
    classes: Optional[List[str]] = None
    attr_name: Optional[str] = None
    attr_value: Optional[str] = None
    attr_op: Optional[str] = None

    def matches(self, node: _Node) -> bool:
        if node.name == "__root__":
            return False
        if self.tag and node.name.lower() != self.tag.lower():
            return False
        if self.id and node.attrs.get("id") != self.id:
            return False
        if self.classes:
            node_classes = node.attrs.get("class", "").split()
            for cls in self.classes:
                if cls not in node_classes:
                    return False
        if self.attr_name:
            attr_val = node.attrs.get(self.attr_name)
            if attr_val is None:
                return False
            if self.attr_op == "=":
                return attr_val == (self.attr_value or "")
            if self.attr_op == "*=" and self.attr_value:
                return self.attr_value in attr_val
        return True


def _parse_selector(selector: str) -> _Selector:
    selector = selector.strip()
    tag: Optional[str] = None
    sel_id: Optional[str] = None
    classes: List[str] = []
    attr_name: Optional[str] = None
    attr_value: Optional[str] = None
    attr_op: Optional[str] = None

    cursor = selector
    while cursor:
        if cursor.startswith("#"):
            match = re.match(r"#([\w-]+)", cursor)
            if not match:
                break
            sel_id = match.group(1)
            cursor = cursor[match.end():]
            continue
        if cursor.startswith("."):
            match = re.match(r"\.([\w-]+)", cursor)
            if not match:
                break
            classes.append(match.group(1))
            cursor = cursor[match.end():]
            continue
        if cursor.startswith("["):
            match = _selector_attr_re.match(cursor)
            if not match:
                break
            attr_name = match.group("name").strip()
            attr_op = match.group("op")
            value = match.group("value")
            if value:
                value = value.strip("\"'")
            attr_value = value
            cursor = cursor[match.end():]
            continue
        match = re.match(r"[a-zA-Z0-9_:-]+", cursor)
        if match:
            tag = match.group(0)
            cursor = cursor[match.end():]
        else:
            break
    return _Selector(
        tag=tag,
        id=sel_id,
        classes=classes or None,
        attr_name=attr_name,
        attr_value=attr_value,
        attr_op=attr_op,
    )


def _iter_nodes(node: _Node, include_self: bool = False) -> Iterator[_Node]:
    if include_self and node.name != "__root__":
        yield node
    for child in node.children:
        if isinstance(child, _Node):
            yield from _iter_nodes(child, include_self=True)


def _match_name(node: _Node, name: NameArg) -> bool:
    if name is None:
        return True
    if callable(name):
        try:
            return bool(name(Tag(node)))
        except Exception:
            return False
    return node.name.lower() == str(name).lower()


def _match_attrs(node: _Node, attrs: AttrsArg) -> bool:
    if not attrs:
        return True
    for key, expected in attrs.items():
        value = node.attrs.get(key)
        if callable(expected):
            try:
                if not expected(value):
                    return False
            except Exception:
                return False
        else:
            if value != expected:
                return False
    return True


class _SoupMixin:
    _node: _Node

    def find(self, name: NameArg = None, attrs: AttrsArg = None) -> Optional["Tag"]:
        for match in self.find_all(name, attrs):
            return match
        return None

    def find_all(self, name: NameArg = None, attrs: AttrsArg = None) -> List["Tag"]:
        matches: List[Tag] = []
        iterator: Iterable[_Node]
        if isinstance(self, BeautifulSoup):
            iterator = _iter_nodes(self._node, include_self=False)
        else:
            iterator = _iter_nodes(self._node, include_self=False)
        for node in iterator:
            if _match_name(node, name) and _match_attrs(node, attrs):
                matches.append(Tag(node))
        return matches

    def select(self, selector: str) -> List["Tag"]:
        selectors = [part.strip() for part in selector.split(",") if part.strip()]
        results: List[Tag] = []
        seen: set[int] = set()
        iterator = list(_iter_nodes(self._node, include_self=isinstance(self, BeautifulSoup)))
        for selector_item in selectors:
            parsed = _parse_selector(selector_item)
            for node in iterator:
                if id(node) in seen:
                    continue
                if parsed.matches(node):
                    seen.add(id(node))
                    results.append(Tag(node))
        return results

    def select_one(self, selector: str) -> Optional["Tag"]:
        matches = self.select(selector)
        return matches[0] if matches else None

    def get_text(self, strip: bool = False) -> str:
        text = self._node.text_content()
        return text.strip() if strip else text

    def decode_contents(self) -> str:
        return self._node.render_contents()


class Tag(_SoupMixin):
    def __init__(self, node: _Node) -> None:
        self._node = node

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Tag name={self.name!r}>"

    @property
    def name(self) -> str:
        return self._node.name

    @property
    def attrs(self) -> Dict[str, str]:
        return dict(self._node.attrs)

    def has_attr(self, key: str) -> bool:
        return key in self._node.attrs

    def __getitem__(self, key: str) -> str:
        return self._node.attrs[key]

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._node.attrs.get(key, default)

    @property
    def next_sibling(self) -> Optional[Union["Tag", str]]:
        parent = self._node.parent
        if not parent:
            return None
        siblings = parent.children
        try:
            index = siblings.index(self._node)
        except ValueError:
            return None
        for sibling in siblings[index + 1 :]:
            if isinstance(sibling, _Node):
                return Tag(sibling)
            if isinstance(sibling, str) and sibling.strip():
                return sibling
        return None


class BeautifulSoup(_SoupMixin):
    def __init__(self, markup: Union[str, bytes], parser: str = "html.parser") -> None:
        if isinstance(markup, bytes):
            markup = markup.decode("utf-8", errors="ignore")
        builder = _HTMLTreeBuilder()
        builder.feed(markup or "")
        builder.close()
        self._node = builder.root

    def find_all(self, name: NameArg = None, attrs: AttrsArg = None) -> List["Tag"]:
        matches: List[Tag] = []
        for node in _iter_nodes(self._node, include_self=False):
            if _match_name(node, name) and _match_attrs(node, attrs):
                matches.append(Tag(node))
        return matches


__all__ = ["BeautifulSoup", "Tag"]
