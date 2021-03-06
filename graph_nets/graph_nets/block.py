from copy import deepcopy
from typing import Optional, Tuple
from torch import nn
from graph_nets.data_structures.graph import Graph
from graph_nets.functions.aggregation import Aggregation, ConstantAggregation
from graph_nets.functions.update import EdgeUpdate, NodeUpdate, GlobalStateUpdate, IdentityEdgeUpdate, \
    IdentityGlobalStateUpdate, IndependentEdgeUpdate, IdentityNodeUpdate, IndependentGlobalStateUpdate, \
    IndependentNodeUpdate


class GNBlock(nn.Module):

    def __init__(self, phi_e: Optional[EdgeUpdate] = None, phi_v: Optional[NodeUpdate] = None,
                 phi_u: Optional[GlobalStateUpdate] = None, rho_ev: Optional[Aggregation] = None,
                 rho_vu: Optional[Aggregation] = None, rho_eu: Optional[Aggregation] = None) -> None:
        """
        Graph network block initialization function.
        All functions are optional. For update functions, the identity update will be used as default. For aggregation
        function, the constant aggregation will be used (i.e. no aggregation happens).
        :param phi_e: Edge update function
        :param phi_v: Node update function
        :param phi_u: Global state update function
        :param rho_ev: Edge aggregation function for nodes
        :param rho_vu: Node aggregation function for the global state
        :param rho_eu: Edge aggregation function for the global state
        """

        super().__init__()

        # default values
        phi_e = phi_e if phi_e else IdentityEdgeUpdate()
        phi_v = phi_v if phi_v else IdentityNodeUpdate()
        phi_u = phi_u if phi_u else IdentityGlobalStateUpdate()
        rho_ev = rho_ev if rho_ev else ConstantAggregation()
        rho_vu = rho_vu if rho_vu else ConstantAggregation()
        rho_eu = rho_eu if rho_eu else ConstantAggregation()

        self.phi_e, self.phi_v, self.phi_u = phi_e, phi_v, phi_u
        self.rho_ev, self.rho_vu, self.rho_eu = rho_ev, rho_vu, rho_eu

    def forward(self, g: Graph) -> Graph:
        """
        Converts a graph g=(u, V, E) into an updated graph g'=(u', V', E') by applying an edge block, a node block, and
        a global block.
        :param g: Input graph g=(u, V, E), will not be modified
        :return: Output graph g'=(u', V', E')
        """

        g = deepcopy(g)

        self._edge_block(g)
        self._node_block(g)
        self._global_block(g)

        return g

    def _edge_block(self, g: Graph) -> None:
        """
        Applies the edge update function to every edge in the graph.
        :param g: Graph to work on (edges will be modified)
        """

        for e in g.edges:
            e.attr = self.phi_e(e=e.attr,
                                     v_r=e.receiver.attr,
                                     v_s=e.sender.attr,
                                     u=g.attr)

    def _node_block(self, g: Graph) -> None:
        """
        Applies the node update function to every node in the graph.
        :param g: Graph to work on (node attributes will be modified)
        """

        for v in g.nodes:
            # aggregate incoming edges (where v is e.r)
            aggr_e = self.rho_ev([e.attr for e in v.receiving_edges])

            # update node
            v.attr = self.phi_v(aggr_e=aggr_e,
                                     v=v.attr,
                                     u=g.attr)

    def _global_block(self, g: Graph) -> None:
        """
        Applies the global state update function to the graph's global state.
        :param g: Graph to work on (global state will be modified)
        """

        u = g.attr

        # aggregate nodes and edges
        aggr_e = self.rho_eu([e.attr for e in g.edges])
        aggr_v = self.rho_vu([n.attr for n in g.nodes])

        # update global state (graph attribute)
        u_prime = self.phi_u(aggr_e=aggr_e, aggr_v=aggr_v, u=u)

        g.attr = u_prime


LinearConfig = Tuple[int, int, bool]
OptLinearConfig = Optional[LinearConfig]


class LinearIndependentGNBlock(nn.Module):
    """
    Graph network block that applies independent linear updates to edges, nodes, and global states.
    Independent means that neighborhood information is disregarded, linear is a linear layer (matmul).
    """

    def __init__(self, e_config: OptLinearConfig = None, v_config: OptLinearConfig = None,
                 u_config: OptLinearConfig = None) -> None:
        """
        For all three parameters, the identity mapping will be used if None is being passed.
        :param e_config: Configuration of the linear layer that is applied to edges
        :param v_config: Configuration of the linear layer that is applied to nodes
        :param u_config: Configuration of the linear layer that is applied to the global state
        """

        super().__init__()

        phi_e = IdentityEdgeUpdate() if e_config is None else IndependentEdgeUpdate(nn.Linear(*e_config))
        phi_v = IdentityNodeUpdate() if v_config is None else IndependentNodeUpdate(nn.Linear(*v_config))
        phi_u = IdentityGlobalStateUpdate() if u_config is None else IndependentGlobalStateUpdate(nn.Linear(*u_config))

        self.block = GNBlock(
            phi_e, phi_v, phi_u,
            rho_ev=ConstantAggregation(),
            rho_vu=ConstantAggregation(),
            rho_eu=ConstantAggregation())

    def forward(self, g: Graph) -> Graph:
        return self.block(g)
