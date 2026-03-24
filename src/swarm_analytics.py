import asyncio
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress' 
    COMPLETED = 'completed'
    FAILED = 'failed'

@dataclass
class SwarmTask:
    task_id: str
    status: TaskStatus
    payload: Any
    assigned_node: str = None
    result: Any = None

class SwarmCoordinator:
    def __init__(self):
        self.tasks: Dict[str, SwarmTask] = {}
        self.nodes: Dict[str, bool] = {}
        self.task_handlers: Dict[str, Callable] = {}
        
    async def register_node(self, node_id: str) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = True
        print(f'Node {node_id} joined the swarm')
        
    async def unregister_node(self, node_id: str) -> None:
        """Remove a node from the swarm"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Reassign tasks from failed node
            self._reassign_tasks(node_id)

    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """Register a handler function for a specific task type"""
        self.task_handlers[task_type] = handler

    async def submit_task(self, task_id: str, task_type: str, payload: Any) -> None:
        """Submit a new task to be processed by the swarm"""
        if task_type not in self.task_handlers:
            raise ValueError(f'No handler registered for task type: {task_type}')
            
        task = SwarmTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            payload=payload
        )
        self.tasks[task_id] = task
        await self._assign_task(task)

    async def _assign_task(self, task: SwarmTask) -> None:
        """Assign task to least loaded node using consensus"""
        available_nodes = [n for n, active in self.nodes.items() if active]
        if not available_nodes:
            return
            
        # Simple round-robin for now, could be enhanced with load metrics
        assigned_node = available_nodes[hash(task.task_id) % len(available_nodes)]
        task.assigned_node = assigned_node
        task.status = TaskStatus.IN_PROGRESS
        
        # Execute task handler
        try:
            handler = self.task_handlers[task.task_id.split('-')[0]]
            task.result = await handler(task.payload)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            print(f'Task {task.task_id} failed: {str(e)}')
            await self._reassign_tasks(assigned_node)

    async def _reassign_tasks(self, failed_node: str) -> None:
        """Reassign tasks from failed node"""
        failed_tasks = [
            task for task in self.tasks.values()
            if task.assigned_node == failed_node and 
            task.status == TaskStatus.IN_PROGRESS
        ]
        
        for task in failed_tasks:
            task.status = TaskStatus.PENDING
            task.assigned_node = None
            await self._assign_task(task)

    async def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current status of a task"""
        if task_id not in self.tasks:
            raise KeyError(f'Task {task_id} not found')
        return self.tasks[task_id].status

    async def get_task_result(self, task_id: str) -> Any:
        """Get result of completed task"""
        if task_id not in self.tasks:
            raise KeyError(f'Task {task_id} not found')
        task = self.tasks[task_id]
        if task.status != TaskStatus.COMPLETED:
            raise ValueError(f'Task {task_id} not completed')
        return task.result