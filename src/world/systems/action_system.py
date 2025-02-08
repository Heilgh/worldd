import random
import math
import traceback
from typing import Dict, List, Optional, Tuple
from ...constants import (
    ENTITY_STATES,
    ENTITY_NEEDS,
    TILE_SIZE,
    RESOURCE_TYPES,
    ENTITY_TYPES
)

class ActionSystem:
    def __init__(self, entity):
        """Initialize action system for an entity"""
        self.entity = entity
        self.current_action = None
        self.action_timer = 0
        self.action_queue = []
        self.last_action_time = 0
        self.action_cooldowns = {}
        
    def update(self, world, dt: float):
        """Update entity actions"""
        try:
            # Update cooldowns
            for action in list(self.action_cooldowns.keys()):
                self.action_cooldowns[action] = max(0, self.action_cooldowns[action] - dt)
                if self.action_cooldowns[action] <= 0:
                    del self.action_cooldowns[action]
            
            # Process current action
            if self.current_action:
                self.action_timer -= dt
                if self.action_timer <= 0:
                    self._complete_action()
                    
            # Start new action if none is active
            elif self.action_queue:
                self._start_next_action()
                
        except Exception as e:
            print(f"Error updating actions: {e}")
            traceback.print_exc()
            
    def add_action(self, action: Dict):
        """Add an action to the queue"""
        try:
            if action.get('type') in ENTITY_STATES:
                self.action_queue.append(action)
                return True
            return False
            
        except Exception as e:
            print(f"Error adding action: {e}")
            traceback.print_exc()
            return False
            
    def clear_actions(self):
        """Clear all queued actions"""
        self.action_queue.clear()
        self.current_action = None
        self.action_timer = 0
        
    def queue_action(self, action: Dict) -> bool:
        """Queue an action with priority"""
        try:
            if not action or 'type' not in action:
                return False
            
            # Check if action type is valid
            action_type = action['type']
            if action_type not in ENTITY_STATES:
                print(f"Invalid action type: {action_type}")
                return False
            
            # Add priority if not present
            if 'priority' not in action:
                action['priority'] = 1.0
            
            # Insert action in priority order
            for i, queued in enumerate(self.action_queue):
                if action['priority'] > queued.get('priority', 1.0):
                    self.action_queue.insert(i, action)
                    return True
                
            # Add to end if lowest priority
            self.action_queue.append(action)
            return True
            
        except Exception as e:
            print(f"Error queueing action: {e}")
            traceback.print_exc()
            return False

    def _start_next_action(self):
        """Start the next action in queue"""
        try:
            if not self.action_queue:
                return
                
            action = self.action_queue.pop(0)
            action_type = action.get('type')
            
            if action_type in ENTITY_STATES:
                state_data = ENTITY_STATES[action_type]
                
                # Check if action is on cooldown
                if action_type in self.action_cooldowns:
                    self.action_queue.insert(0, action)  # Put back in queue
                    return
                    
                # Check if prerequisites are met
                if not self._check_action_prerequisites(action):
                    return
                    
                # Set current action
                self.current_action = action
                duration = state_data.get('duration', (5, 15))
                if isinstance(duration, tuple):
                    self.action_timer = random.uniform(duration[0], duration[1])
                else:
                    self.action_timer = duration
                    
                # Apply initial effects
                self._apply_action_effects(action_type, state_data)
                
                # Set cooldown
                self.action_cooldowns[action_type] = state_data.get('cooldown', 0)
                
                # Update entity state
                self.entity.state['current'] = action_type
                self.entity.state['target'] = action.get('target')
                
        except Exception as e:
            print(f"Error starting action: {e}")
            traceback.print_exc()
            
    def _check_action_prerequisites(self, action: Dict) -> bool:
        """Check if prerequisites for an action are met"""
        try:
            action_type = action.get('type')
            
            # Check energy requirements
            if action_type in ENTITY_STATES:
                energy_cost = ENTITY_STATES[action_type].get('energy_cost', 0)
                if self.entity.energy < energy_cost:
                    return False
                    
            # Check target validity
            target = action.get('target')
            if target:
                if action_type == 'move':
                    return self._is_valid_move_target(target)
                elif action_type == 'interact':
                    return self._is_valid_interaction_target(target)
                elif action_type == 'gather':
                    return self._is_valid_gather_target(target)
                    
            return True
            
        except Exception as e:
            print(f"Error checking action prerequisites: {e}")
            traceback.print_exc()
            return False

    def _is_valid_move_target(self, target) -> bool:
        """Check if move target is valid"""
        try:
            # Check if target is within world bounds
            if not self.entity.world:
                return False
            
            x, y = target
            if not (0 <= x < self.entity.world.width and 0 <= y < self.entity.world.height):
                return False
            
            # Check if target is walkable
            tile = self.entity.world.get_tile_at(x, y)
            if not tile or not tile.get('walkable', False):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking move target: {e}")
            traceback.print_exc()
            return False

    def _is_valid_interaction_target(self, target) -> bool:
        """Check if interaction target is valid"""
        try:
            if not target or not hasattr(target, 'x') or not hasattr(target, 'y'):
                return False
            
            # Check if target is within interaction range
            dx = target.x - self.entity.x
            dy = target.y - self.entity.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            return distance <= TILE_SIZE * 2  # 2 tiles interaction range
            
        except Exception as e:
            print(f"Error checking interaction target: {e}")
            traceback.print_exc()
            return False

    def _is_valid_gather_target(self, target) -> bool:
        """Check if gather target is valid"""
        try:
            if not target or 'type' not in target:
                return False
            
            # Check if target is a valid resource
            resource_type = target['type']
            if resource_type not in RESOURCE_TYPES:
                return False
            
            # Check if entity has required tool
            required_tool = RESOURCE_TYPES[resource_type].get('tool_required')
            if required_tool and not self._has_tool(required_tool):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking gather target: {e}")
            traceback.print_exc()
            return False

    def _has_tool(self, tool_type: str) -> bool:
        """Check if entity has a specific tool"""
        try:
            if not hasattr(self.entity, 'equipment'):
                return False
            
            return any(item.get('type') == tool_type for item in self.entity.equipment.values())
            
        except Exception as e:
            print(f"Error checking tool: {e}")
            traceback.print_exc()
            return False

    def _apply_action_effects(self, action_type: str, state_data: Dict):
        """Apply effects when starting an action"""
        try:
            # Apply energy cost
            if 'energy_cost' in state_data:
                self.entity.energy = max(0, self.entity.energy - state_data['energy_cost'])
                
            # Apply state-specific effects
            if action_type == 'moving':
                self._start_movement()
            elif action_type == 'interacting':
                self._start_interaction()
            elif action_type == 'gathering':
                self._start_gathering()
            elif action_type == 'resting':
                self._start_resting()
            elif action_type == 'crafting':
                self._start_crafting()
                
        except Exception as e:
            print(f"Error applying action effects: {e}")
            traceback.print_exc()
            
    def _start_movement(self):
        """Start movement action"""
        try:
            if not self.current_action or 'target' not in self.current_action:
                return
            
            target = self.current_action['target']
            self.entity.state['path'] = self._find_path(target)
            self.entity.state['current'] = 'moving'
            
        except Exception as e:
            print(f"Error starting movement: {e}")
            traceback.print_exc()

    def _start_interaction(self):
        """Start interaction action"""
        try:
            if not self.current_action or 'target' not in self.current_action:
                return
            
            target = self.current_action['target']
            interaction = self.current_action.get('interaction', 'default')
            
            self.entity.state['current'] = 'interacting'
            self.entity.state['interaction_type'] = interaction
            self.entity.state['interaction_target'] = target
            
        except Exception as e:
            print(f"Error starting interaction: {e}")
            traceback.print_exc()

    def _start_gathering(self):
        """Start gathering action"""
        try:
            if not self.current_action or 'target' not in self.current_action:
                return
            
            target = self.current_action['target']
            self.entity.state['current'] = 'gathering'
            self.entity.state['gather_target'] = target
            self.entity.state['gather_progress'] = 0
            
        except Exception as e:
            print(f"Error starting gathering: {e}")
            traceback.print_exc()

    def _start_resting(self):
        """Start resting action"""
        try:
            self.entity.state['current'] = 'resting'
            self.entity.state['rest_start_time'] = self.entity.world.time_system['time']
            
        except Exception as e:
            print(f"Error starting rest: {e}")
            traceback.print_exc()

    def _start_crafting(self):
        """Start crafting action"""
        try:
            if not self.current_action or 'recipe' not in self.current_action:
                return
            
            recipe = self.current_action['recipe']
            self.entity.state['current'] = 'crafting'
            self.entity.state['craft_recipe'] = recipe
            self.entity.state['craft_progress'] = 0
            
        except Exception as e:
            print(f"Error starting crafting: {e}")
            traceback.print_exc()

    def _complete_action(self):
        """Complete the current action"""
        try:
            if self.current_action:
                action_type = self.current_action.get('type')
                
                # Apply completion effects
                if action_type in ENTITY_STATES:
                    state_data = ENTITY_STATES[action_type]
                    self._apply_completion_effects(action_type, state_data)
                    
            # Clear current action
            self.current_action = None
            self.action_timer = 0
            
        except Exception as e:
            print(f"Error completing action: {e}")
            traceback.print_exc()
            
    def _apply_completion_effects(self, action_type: str, state_data: Dict):
        """Apply effects when completing an action"""
        try:
            # Apply energy gain
            if 'energy_gain' in state_data:
                self.entity.energy = min(100, self.entity.energy + state_data['energy_gain'])
                
            # Apply need reductions
            if 'hunger_reduction' in state_data:
                self.entity.needs['hunger'] = max(0, self.entity.needs['hunger'] - state_data['hunger_reduction'])
            if 'thirst_reduction' in state_data:
                self.entity.needs['thirst'] = max(0, self.entity.needs['thirst'] - state_data['thirst_reduction'])
                
            # Apply action-specific completion effects
            if action_type == 'moving':
                self._complete_movement()
            elif action_type == 'interacting':
                self._complete_interaction()
            elif action_type == 'gathering':
                self._complete_gathering()
            elif action_type == 'resting':
                self._complete_resting()
            elif action_type == 'crafting':
                self._complete_crafting()
                
            # Reset state
            self.entity.state['current'] = 'idle'
            self.entity.state['target'] = None
            
        except Exception as e:
            print(f"Error applying completion effects: {e}")
            traceback.print_exc()
            
    def _complete_movement(self):
        """Complete movement action"""
        try:
            # Clear path
            self.entity.state['path'] = []
            
            # Start next action if queued
            next_action = self.current_action.get('next_action')
            if next_action:
                self.queue_action(next_action)
            
        except Exception as e:
            print(f"Error completing movement: {e}")
            traceback.print_exc()

    def _complete_interaction(self):
        """Complete interaction action"""
        try:
            target = self.entity.state.get('interaction_target')
            interaction_type = self.entity.state.get('interaction_type')
            
            if target and interaction_type:
                # Update relationship if target is human
                if hasattr(target, 'id') and target.id in self.entity.social['relationships']:
                    relationship = self.entity.social['relationships'][target.id]
                    relationship['last_interaction'] = self.entity.world.time_system['time']
                    
                    # Adjust relationship value based on interaction
                    if interaction_type == 'chat':
                        relationship['value'] = min(100, relationship['value'] + 5)
                    elif interaction_type == 'help':
                        relationship['value'] = min(100, relationship['value'] + 10)
                        
            # Clear interaction state
            self.entity.state['interaction_target'] = None
            self.entity.state['interaction_type'] = None
            
        except Exception as e:
            print(f"Error completing interaction: {e}")
            traceback.print_exc()

    def _complete_gathering(self):
        """Complete gathering action"""
        try:
            target = self.entity.state.get('gather_target')
            if target and 'type' in target:
                # Add resource to inventory
                if hasattr(self.entity, 'inventory'):
                    self.entity.inventory.append({
                        'type': target['type'],
                        'quantity': random.randint(1, 5),
                        'quality': random.uniform(0.5, 1.0)
                    })
                    
            # Clear gathering state
            self.entity.state['gather_target'] = None
            self.entity.state['gather_progress'] = 0
            
        except Exception as e:
            print(f"Error completing gathering: {e}")
            traceback.print_exc()

    def _complete_resting(self):
        """Complete resting action"""
        try:
            rest_start = self.entity.state.get('rest_start_time', 0)
            current_time = self.entity.world.time_system['time']
            rest_duration = current_time - rest_start
            
            # Apply rest benefits
            energy_gain = min(50, rest_duration * 0.1)  # 10% energy per second
            self.entity.energy = min(100, self.entity.energy + energy_gain)
            
            # Clear rest state
            self.entity.state['rest_start_time'] = 0
            
        except Exception as e:
            print(f"Error completing rest: {e}")
            traceback.print_exc()

    def _complete_crafting(self):
        """Complete crafting action"""
        try:
            recipe = self.entity.state.get('craft_recipe')
            if recipe and hasattr(self.entity, 'inventory'):
                # Add crafted item to inventory
                self.entity.inventory.append({
                    'type': recipe,
                    'quantity': 1,
                    'quality': random.uniform(0.5, 1.0)
                })
                
            # Clear crafting state
            self.entity.state['craft_recipe'] = None
            self.entity.state['craft_progress'] = 0
            
        except Exception as e:
            print(f"Error completing crafting: {e}")
            traceback.print_exc()

    def get_current_action(self) -> Optional[Dict]:
        """Get the current action"""
        return self.current_action
        
    def has_action(self, action_type: str) -> bool:
        """Check if an action type is in the queue"""
        return any(a.get('type') == action_type for a in self.action_queue)
        
    def is_busy(self) -> bool:
        """Check if entity is currently performing an action"""
        return self.current_action is not None