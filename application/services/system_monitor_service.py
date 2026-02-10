from typing import Dict, Optional
import time

from domain.ports.node_input_port import NodeInputPort
from domain.models.node import Node
from domain.value_objects.parameter import Parameter
from domain.ports.module_query_port import ModuleQueryPort
from domain.ports.node_query_port import NodeQueryPort
from domain.ports.node_input_port import NodeInputPort
from application.ports.system_status import SystemStatusPort
from application.dto import ElectricalPointStatus, NodeStatus

class SystemMonitorService:
    """
    Application / Domain Service:
    Theo dõi, cập nhật và tổng hợp trạng thái toàn hệ thống
    """

    def __init__(
        self,
        node_port: NodeQueryPort,
        module_port: ModuleQueryPort,
        param_port: NodeInputPort,
        status_port: SystemStatusPort,
    ):
        self.nodes = {}
        self.node_port = node_port
        self.module_port = module_port
        self.param_port = param_port
        self.status_port = status_port
        self.init_nodes()

    def init_nodes(self):
        for node in self.node_port.load_nodes():
            modules = self.module_port.load_modules_for_node(node.name)
            for module in modules:
                node.add_module(module)
            self.nodes[node.node_id] = node
        
    def register_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node
        
    def get_node(self, node_id: int) -> Optional[Node]:
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> Dict[int, Node]:
        return self.nodes
    
    def update_node_voltage(self):
        """
        Cập nhật điện áp node thông qua port
        """
        node_id, voltage_value = self.param_port.on_voltage_update()
        
        node = self.get_node(node_id)
        if not node:
            return

        voltage = Parameter("voltage", voltage_value, "V")
        node.set_voltage(voltage)
        node.last_update_time = time.time()
        
    def update_module_parameter(self):
        """
        Cập nhật thông số của module trong node thông qua port
        """
        node_id, module_id, parameters = self.param_port.on_module_parameters_update()
        node = self.get_node(node_id)
        if not node:
            return

        module = node.modules.get(module_id)
        if not module:
            return

        for name, param in parameters.items():
            module.update_parameter(param)
    
    def recalculate_node_status(self, node_id: int):
        node = self.get_node(node_id)
        if not node:
            return
        
        node.recalculate_status()
        self.status_port.present_node_status(NodeStatus(node_id, node.has_error))
            
    def recalculate_all_nodes(self):
        for node in self.nodes.values():
            node.recalculate_status()