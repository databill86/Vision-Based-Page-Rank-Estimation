import torch
from typing import Set, Optional, List, Dict
from .attribute import Attribute


class Node:
    """
    A node in a graph. It has an attribute that can hold any value.
    """

    def __init__(self, attr: Optional[Attribute] = None) -> None:
        if attr is None:
            attr = Attribute(val=None)

        self.attr = attr  # v
        from .edge import Edge
        self.receiving_edges: Set[Edge] = set()  # incoming
        self.sending_edges: Set[Edge] = set()  # outgoing

    def to(self, device: torch.device) -> 'Node':
        """
        Moves torch values of this object to the specified device (e.g. GPU).
        """
        self.attr.to(device)
        return self

    def asdict(self) -> Dict:
        return {
            'attr': self.attr.asdict()
        }

    @staticmethod
    def from_dict(d: Dict) -> 'Node':
        return Node(Attribute.from_dict(d['attr']))

    def __repr__(self) -> str:
        return "node({})".format(self.attr.__repr__())

    @staticmethod
    def from_vals(vals: List[any]) -> List['Node']:
        return [Node(Attribute(x)) for x in vals]

    @staticmethod
    def eq_attr(n1: 'Node', n2: 'Node') -> bool:
        """
        Equality check for two nodes. Does not compare receiving and sending edges, i.e. it disregards the context.
        """
        return n1.attr == n2.attr
