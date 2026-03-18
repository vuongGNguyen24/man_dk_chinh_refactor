from application.dto import NodeStatus, NodeParameter, ModuleParameter, ModuleStatus

class SystemStatusPort:

    def present_node_status(self, dto: NodeStatus) -> None:
        raise NotImplementedError
    
    def present_node_parameter(self, dto: NodeParameter) -> None:
        raise NotImplementedError
    
    def present_module_status(self, dto: ModuleStatus) -> None:
        raise NotImplementedError
    
    def present_module_parameter(self, dto: ModuleParameter) -> None:
        raise NotImplementedError
