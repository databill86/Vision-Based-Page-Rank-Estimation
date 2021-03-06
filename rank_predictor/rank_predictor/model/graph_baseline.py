import torch
from typing import Dict
from torch import nn
from graph_nets.block import GNBlock
from graph_nets.data_structures.attribute import Attribute
from graph_nets.data_structures.graph import Graph
from graph_nets.functions.aggregation import ConstantAggregation, AvgAggregation
from graph_nets.functions.update import IdentityEdgeUpdate, IndependentNodeUpdate, NodeAggregationGlobalStateUpdate
from rank_predictor.model.screenshot_feature_extractor import DesktopScreenshotFeatureExtractor


class GraphBaseline(nn.Module):

    def __init__(self):
        super().__init__()

        self.desktop_screenshot_extractor = DesktopScreenshotFeatureExtractor()

        def node_update_fn(node: Dict[str, any]) -> Attribute:
            desktop_img: torch.Tensor = node['desktop_img']

            rank_scalar = self.desktop_screenshot_extractor(desktop_img.unsqueeze(0))

            return rank_scalar

        self.graph_block = GNBlock(
            phi_e=IdentityEdgeUpdate(),
            phi_v=IndependentNodeUpdate(node_update_fn),
            phi_u=NodeAggregationGlobalStateUpdate(),
            rho_ev=ConstantAggregation(),
            rho_vu=AvgAggregation(),
            rho_eu=ConstantAggregation())

    def forward(self, g: Graph) -> Graph:
        g_out: Graph = self.graph_block(g)
        return g_out.attr.val
