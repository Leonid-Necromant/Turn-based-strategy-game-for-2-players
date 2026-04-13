import pygame
import random
import uuid
import math
import os
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass

pygame.init()
CELL_SIZE = 55
INFO_PANEL_WIDTH = 350
WINDOW_WIDTH = 15 * CELL_SIZE + INFO_PANEL_WIDTH
WINDOW_HEIGHT = 15 * CELL_SIZE
FPS = 60
class Colors:
    RED = (255, 80, 80)
    BLUE = (80, 80, 255)
    GREEN = (34, 139, 34)
    WATER = (100, 150, 255)
    WATER_DARK = (50, 100, 200)
    GRASS_DARK = (0, 100, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (240, 240, 240)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW_HIGHLIGHT = (255, 255, 0, 100)
    RED_HIGHLIGHT = (255, 0, 0, 100)

class ImageLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.images = {}
            cls._instance.load_all_images()
        return cls._instance
    
    def load_all_images(self):
        if not os.path.exists("draw"):
            os.makedirs("draw")
            self.create_default_images()

        unit_files = {
            "archer": "archer.png",
            "catapult": "catapult.png",
            "horseman": "horseman.png",
            "swordsman": "swordsman.png"
        }
        
        for unit_name, filename in unit_files.items():
            path = os.path.join("draw", filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))
                    self.images[f"unit_{unit_name}"] = img
                    print(f"Загружено изображение: {filename}")
                except pygame.error as e:
                    print(f"Ошибка загрузки {filename}: {e}")
                    self.images[f"unit_{unit_name}"] = None
            else:
                print(f"Файл не найден: {path}")
                self.images[f"unit_{unit_name}"] = None
        
        terrain_files = {
            "grass": "grass.png",
            "water": "water.png"
        }
        
        for terrain_name, filename in terrain_files.items():
            path = os.path.join("draw", filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                    self.images[f"terrain_{terrain_name}"] = img
                    print(f"Загружено изображение: {filename}")
                except pygame.error as e:
                    print(f"Ошибка загрузки {filename}: {e}")
                    self.images[f"terrain_{terrain_name}"] = None
            else:
                print(f"Файл не найден: {path}")
                self.images[f"terrain_{terrain_name}"] = None
    
    def create_default_images(self):
        grass_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        grass_surf.fill(Colors.GREEN)
        for _ in range(50):
            x = random.randint(0, CELL_SIZE - 1)
            y = random.randint(0, CELL_SIZE - 1)
            grass_surf.set_at((x, y), Colors.GRASS_DARK)
        pygame.image.save(grass_surf, os.path.join("draw", "grass.png"))
        
        water_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        water_surf.fill(Colors.WATER)

        for i in range(3):
            y = 15 + i * 15
            pygame.draw.line(water_surf, Colors.WATER_DARK, (5, y), (CELL_SIZE - 5, y), 2)
        pygame.image.save(water_surf, os.path.join("draw", "water.png"))
        
        unit_colors = {
            "archer": (255, 200, 100),
            "catapult": (150, 150, 150),
            "horseman": (200, 100, 50),
            "swordsman": (100, 100, 200)
        }
        
        for unit_name, color in unit_colors.items():
            unit_surf = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
            pygame.draw.circle(unit_surf, color, (22, 22), 20)
            pygame.draw.circle(unit_surf, Colors.BLACK, (22, 22), 20, 2)
            
            font = pygame.font.Font(None, 30)
            symbol = unit_name[0].upper()
            text = font.render(symbol, True, Colors.BLACK)
            text_rect = text.get_rect(center=(22, 22))
            unit_surf.blit(text, text_rect)
            
            pygame.image.save(unit_surf, os.path.join("draw", f"{unit_name}.png"))
        
        print("Созданы изображения по умолчанию в папке draw")
    
    def get_unit_image(self, unit_type: str) -> Optional[pygame.Surface]:
        return self.images.get(f"unit_{unit_type.lower()}")
    
    def get_terrain_image(self, terrain_type: str) -> Optional[pygame.Surface]:
        return self.images.get(f"terrain_{terrain_type.lower()}")

@dataclass
class Coordinates:
    x: int
    y: int
    
    def distance_to(self, other: 'Coordinates') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

class MapObject(ABC):
    @abstractmethod
    def is_passable(self) -> bool: pass
    
    @abstractmethod
    def is_occupiable(self) -> bool: pass
    
    @abstractmethod
    def get_type(self) -> str: pass

class Terrain(MapObject, ABC):
    def __init__(self, coordinates: Optional[Coordinates] = None):
        self.coordinates = coordinates
        self.x = coordinates.x if coordinates else 0
        self.y = coordinates.y if coordinates else 0
    
    def get_coordinates(self) -> Optional[Coordinates]:
        return self.coordinates
    
    def is_occupiable(self) -> bool:
        return self.is_passable()
    
    def set_x(self, x: int):
        self.x = x
        self.coordinates = Coordinates(x, self.y)
    
    def set_y(self, y: int):
        self.y = y
        self.coordinates = Coordinates(self.x, y)

class Grass(Terrain):
    def __init__(self, coordinates: Optional[Coordinates] = None):
        super().__init__(coordinates)
    
    def is_passable(self) -> bool:
        return True
    
    def get_type(self) -> str:
        return "Grass"

class Water(Terrain):
    def __init__(self, coordinates: Optional[Coordinates] = None):
        super().__init__(coordinates)
    
    def is_passable(self) -> bool:
        return False
    
    def get_type(self) -> str:
        return "Water"

class Player:
    def __init__(self, id: int, name: str, color: Tuple[int, int, int]):
        self.id = id
        self.name = name
        self.color = color
        self.units: List['Unit'] = []
    
    def add_unit(self, unit: 'Unit'):
        self.units.append(unit)
    
    def remove_unit(self, unit: 'Unit'):
        if unit in self.units:
            self.units.remove(unit)
    
    def get_alive_units(self) -> List['Unit']:
        return [unit for unit in self.units if unit.is_alive()]

class Unit(MapObject, ABC):
    def __init__(self, id: str, owner: Player, coordinates: Optional[Coordinates], max_health: int):
        self.id = id
        self.owner = owner
        self.coordinates = coordinates
        self.health = max_health
        self.max_health = max_health
        self.movement_left = 0
        self.x = coordinates.x if coordinates else 0
        self.y = coordinates.y if coordinates else 0
        
        if coordinates:
            self.x = coordinates.x
            self.y = coordinates.y
    
    def reset_turn(self):
        self.movement_left = self.get_movement_range()
    
    def has_movement_left(self) -> bool:
        return self.movement_left > 0
    
    def get_coordinates(self) -> Optional[Coordinates]:
        return self.coordinates
    
    def set_coordinates(self, coordinates: Coordinates):
        self.coordinates = coordinates
        if coordinates:
            self.x = coordinates.x
            self.y = coordinates.y
    
    def get_x(self) -> int:
        return self.x
    
    def get_y(self) -> int:
        return self.y
    
    def set_x(self, x: int):
        self.x = x
        self.coordinates = Coordinates(x, self.y)
    
    def set_y(self, y: int):
        self.y = y
        self.coordinates = Coordinates(self.x, y)
    
    def get_health(self) -> int:
        return self.health
    
    def get_max_health(self) -> int:
        return self.max_health
    
    def is_alive(self) -> bool:
        return self.health > 0
    
    def is_passable(self) -> bool:
        return False
    
    def is_occupiable(self) -> bool:
        return False
    
    @abstractmethod
    def get_movement_range(self) -> int: pass
    
    @abstractmethod
    def get_attack_range(self) -> int: pass
    
    @abstractmethod
    def get_melee_damage(self) -> int: pass
    
    @abstractmethod
    def get_ranged_damage(self) -> int: pass
    
    @abstractmethod
    def can_attack_at_distance(self, distance: float) -> bool: pass
    
    @abstractmethod
    def get_unit_symbol(self) -> str: pass
    
    def get_image_name(self) -> str:
        return self.get_type().lower()
    
    def take_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def calculate_damage(self, target: 'Unit') -> int:
        distance = self.coordinates.distance_to(target.get_coordinates())
        if not self.can_attack_at_distance(distance):
            return 0
        return self.get_melee_damage() if distance <= 1.5 else self.get_ranged_damage()
    
    def attack(self, target: 'Unit'):
        if target is None or target.owner == self.owner:
            return
        target.take_damage(self.calculate_damage(target))
    
    def can_move_to(self, new_coordinates: Coordinates, game_map: 'GameMap') -> bool:
        if new_coordinates is None:
            return False
        distance = self.coordinates.distance_to(new_coordinates)
        if distance > self.get_movement_range() + 0.1:
            return False
        return game_map.is_cell_passable(new_coordinates) and not game_map.is_cell_occupied(new_coordinates)

class Archer(Unit):
    def __init__(self, owner: Player, coordinates: Optional[Coordinates] = None, id: Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), owner, coordinates, 50)
    
    def get_movement_range(self) -> int: return 3
    def get_attack_range(self) -> int: return 5
    def get_melee_damage(self) -> int: return 25
    def get_ranged_damage(self) -> int: return 50
    def can_attack_at_distance(self, distance: float) -> bool: return distance <= 5 + 0.1
    def get_type(self) -> str: return "Archer"
    def get_unit_symbol(self) -> str: return "A"

class Catapult(Unit):
    def __init__(self, owner: Player, coordinates: Optional[Coordinates] = None, id: Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), owner, coordinates, 75)
    
    def get_movement_range(self) -> int: return 1
    def get_attack_range(self) -> int: return 10
    def get_melee_damage(self) -> int: return 50
    def get_ranged_damage(self) -> int: return 100
    def can_attack_at_distance(self, distance: float) -> bool: return distance <= 10 + 0.1
    def get_type(self) -> str: return "Catapult"
    def get_unit_symbol(self) -> str: return "C"

class Horseman(Unit):
    def __init__(self, owner: Player, coordinates: Optional[Coordinates] = None, id: Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), owner, coordinates, 200)
    
    def get_movement_range(self) -> int: return 10
    def get_attack_range(self) -> int: return 1
    def get_melee_damage(self) -> int: return 75
    def get_ranged_damage(self) -> int: return 0
    def can_attack_at_distance(self, distance: float) -> bool: return distance <= 1 + 0.1
    def get_type(self) -> str: return "Horseman"
    def get_unit_symbol(self) -> str: return "H"

class Swordsman(Unit):
    def __init__(self, owner: Player, coordinates: Optional[Coordinates] = None, id: Optional[str] = None):
        super().__init__(id or str(uuid.uuid4()), owner, coordinates, 100)
    
    def get_movement_range(self) -> int: return 5
    def get_attack_range(self) -> int: return 1
    def get_melee_damage(self) -> int: return 50
    def get_ranged_damage(self) -> int: return 0
    def can_attack_at_distance(self, distance: float) -> bool: return distance <= 1 + 0.1
    def get_type(self) -> str: return "Swordsman"
    def get_unit_symbol(self) -> str: return "S"


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.terrains: List[List[Terrain]] = [[Grass(Coordinates(x, y)) for x in range(width)] for y in range(height)]
        self.units: Dict[Coordinates, Unit] = {}
    
    def get_width(self) -> int: return self.width
    def get_height(self) -> int: return self.height
    
    def set_terrain(self, coordinates: Coordinates, terrain: Terrain):
        if self.is_valid_coordinates(coordinates):
            self.terrains[coordinates.y][coordinates.x] = terrain
    
    def get_terrain(self, coordinates: Coordinates) -> Optional[Terrain]:
        if self.is_valid_coordinates(coordinates):
            return self.terrains[coordinates.y][coordinates.x]
        return None
    
    def is_valid_coordinates(self, coordinates: Coordinates) -> bool:
        return (coordinates is not None and 
                0 <= coordinates.x < self.width and 
                0 <= coordinates.y < self.height)
    
    def is_cell_passable(self, coordinates: Coordinates) -> bool:
        terrain = self.get_terrain(coordinates)
        return terrain is not None and terrain.is_passable()
    
    def is_cell_occupied(self, coordinates: Coordinates) -> bool:
        return coordinates in self.units
    
    def get_unit_at(self, coordinates: Coordinates) -> Optional[Unit]:
        return self.units.get(coordinates)
    
    def place_unit(self, unit: Unit, coordinates: Coordinates):
        if self.is_cell_passable(coordinates) and not self.is_cell_occupied(coordinates):
            self.units[coordinates] = unit
            unit.set_coordinates(coordinates)
    
    def move_unit(self, unit: Unit, new_coordinates: Coordinates):
        if unit.get_coordinates() in self.units:
            del self.units[unit.get_coordinates()]
            self.units[new_coordinates] = unit
            unit.set_coordinates(new_coordinates)
    
    def remove_unit(self, unit: Unit):
        if unit.get_coordinates() in self.units:
            del self.units[unit.get_coordinates()]
    
    def get_all_units(self) -> List[Unit]:
        return list(self.units.values())


class GameController:
    def __init__(self, map_width: int, map_height: int):
        self.game_map = GameMap(map_width, map_height)
        self.player1 = Player(1, "Красный", Colors.RED)
        self.player2 = Player(2, "Синий", Colors.BLUE)
        self.current_player = self.player1
    
    def get_map(self) -> GameMap: return self.game_map
    def get_player1(self) -> Player: return self.player1
    def get_player2(self) -> Player: return self.player2
    def get_current_player(self) -> Player: return self.current_player
    
    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        for unit in self.current_player.get_alive_units():
            unit.reset_turn()
    
    def create_unit(self, unit_type: str, owner: Player, coordinates: Coordinates) -> Optional[Unit]:
        if not self.game_map.is_valid_coordinates(coordinates) or self.game_map.is_cell_occupied(coordinates):
            return None
        
        unit_id = str(uuid.uuid4())
        unit = None
        
        unit_type = unit_type.lower()
        if unit_type == "archer":
            unit = Archer(owner, coordinates, unit_id)
        elif unit_type == "catapult":
            unit = Catapult(owner, coordinates, unit_id)
        elif unit_type == "horseman":
            unit = Horseman(owner, coordinates, unit_id)
        elif unit_type == "swordsman":
            unit = Swordsman(owner, coordinates, unit_id)
        
        if unit:
            self.game_map.place_unit(unit, coordinates)
            owner.add_unit(unit)
        
        return unit
    
    def move_unit(self, unit: Unit, target: Coordinates) -> bool:
        if (unit is None or not unit.is_alive() or unit.owner != self.current_player):
            return False
        if not unit.can_move_to(target, self.game_map):
            return False
        self.game_map.move_unit(unit, target)
        return True
    
    def attack(self, attacker: Unit, target: Unit) -> bool:
        if (attacker is None or target is None or 
            attacker.owner == target.owner or 
            attacker.owner != self.current_player or 
            not attacker.is_alive() or not target.is_alive()):
            return False
        
        distance = attacker.get_coordinates().distance_to(target.get_coordinates())
        if not attacker.can_attack_at_distance(distance):
            return False
        
        attacker.attack(target)
        if not target.is_alive():
            self.game_map.remove_unit(target)
            target.owner.remove_unit(target)
        return True
    
    def is_game_over(self) -> bool:
        return (len(self.player1.get_alive_units()) == 0 or 
                len(self.player2.get_alive_units()) == 0)
    
    def get_winner(self) -> Optional[Player]:
        if len(self.player1.get_alive_units()) == 0:
            return self.player2
        if len(self.player2.get_alive_units()) == 0:
            return self.player1
        return None
    
    def create_default_terrain(self):
        rnd = random.Random()
        rivers_count = 2
        
        for _ in range(rivers_count):
            horizontal = rnd.choice([True, False])
            gap_size = 2
            gap_start = rnd.randint(0, (self.game_map.width - gap_size if horizontal else self.game_map.height - gap_size) - 1)
            
            if horizontal:
                y = rnd.randint(0, self.game_map.height - 1)
                for x in range(self.game_map.width):
                    if gap_start <= x < gap_start + gap_size:
                        continue
                    
                    self.game_map.set_terrain(
                        Coordinates(x, y),
                        Water(Coordinates(x, y))
                    )
                    
                    if rnd.randint(0, 4) == 0:
                        y += 1 if rnd.choice([True, False]) else -1
                        y = max(0, min(self.game_map.height - 1, y))
            else:
                x = rnd.randint(0, self.game_map.width - 1)
                for y in range(self.game_map.height):
                    if gap_start <= y < gap_start + gap_size:
                        continue
                    
                    self.game_map.set_terrain(
                        Coordinates(x, y),
                        Water(Coordinates(x, y))
                    )
                    
                    if rnd.randint(0, 4) == 0:
                        x += 1 if rnd.choice([True, False]) else -1
                        x = max(0, min(self.game_map.width - 1, x))

class UnitInfoPanel:
    def __init__(self, rect: pygame.Rect, unit: Unit, game: GameController, 
                 on_select: callable, on_attack_click: callable):
        self.rect = rect
        self.unit = unit
        self.game = game
        self.on_select = on_select
        self.on_attack_click = on_attack_click
        self.selected = False
        self.image_loader = ImageLoader()
        
        self.surface = pygame.Surface((rect.width, rect.height))
        self.font = pygame.font.Font(None, 20)
        self.symbol_font = pygame.font.Font(None, 30)
    
    def handle_click(self, pos: Tuple[int, int]):
        if self.rect.collidepoint(pos):
            if (self.unit.owner == self.game.get_current_player() and 
                self.unit.is_alive()):
                self.on_select(self.unit)
    
    def draw(self, screen: pygame.Surface):
        self.surface.fill(Colors.WHITE)
        pygame.draw.rect(self.surface, Colors.GRAY, self.surface.get_rect(), 1)
        

        unit_image = self.image_loader.get_unit_image(self.unit.get_image_name())
        if unit_image:
            
            img_rect = unit_image.get_rect()
            img_rect.topleft = (5, 5)
            self.surface.blit(unit_image, img_rect)
            
            
            info = f"{self.unit.get_type()} ({self.unit.get_health()}/{self.unit.get_max_health()})"
            text = self.font.render(info, True, Colors.BLACK)
            self.surface.blit(text, (45, 15))
        else:
            
            info = f"{self.unit.get_unit_symbol()} {self.unit.get_type()} ({self.unit.get_health()}/{self.unit.get_max_health()})"
            text = self.font.render(info, True, Colors.BLACK)
            self.surface.blit(text, (5, 15))
        
        screen.blit(self.surface, self.rect)

class MapCell:
    def __init__(self, rect: pygame.Rect, coordinates: Coordinates, game: GameController,
                 on_click: callable):
        self.rect = rect
        self.coordinates = coordinates
        self.game = game
        self.on_click = on_click
        self.is_highlighted = False
        self.is_attack_highlight = False
        self.image_loader = ImageLoader()
        
        
        self.symbol_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 16)
    
    def handle_click(self, pos: Tuple[int, int]):
        if self.rect.collidepoint(pos):
            self.on_click(self.coordinates)
    
    def draw(self, screen: pygame.Surface):
        
        terrain = self.game.get_map().get_terrain(self.coordinates)
        
        
        if isinstance(terrain, Water):
            terrain_image = self.image_loader.get_terrain_image("water")
            if terrain_image:
                screen.blit(terrain_image, self.rect)
            else:
                
                pygame.draw.rect(screen, Colors.WATER, self.rect)
                water_text = self.symbol_font.render(" ", True, Colors.WATER_DARK)
                screen.blit(water_text, (self.rect.x + 15, self.rect.y + 10))
        else:  
            terrain_image = self.image_loader.get_terrain_image("grass")
            if terrain_image:
                screen.blit(terrain_image, self.rect)
            else:
                
                pygame.draw.rect(screen, Colors.GREEN, self.rect)
                
                for _ in range(3):
                    x = self.rect.x + random.randint(5, 45)
                    y = self.rect.y + random.randint(5, 45)
                    pygame.draw.line(screen, Colors.GRASS_DARK, (x, y), (x, y-5))
        
        if self.is_attack_highlight:
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 0, 0, 100))
            screen.blit(highlight, self.rect)
        elif self.is_highlighted:
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 0, 100))
            screen.blit(highlight, self.rect)
        
        unit = self.game.get_map().get_unit_at(self.coordinates)
        if unit and unit.is_alive():
            pygame.draw.rect(screen, unit.owner.color, self.rect, 3)
            unit_image = self.image_loader.get_unit_image(unit.get_image_name())
            if unit_image:
                img_x = self.rect.x + (CELL_SIZE - unit_image.get_width()) // 2
                img_y = self.rect.y + (CELL_SIZE - unit_image.get_height()) // 2
                screen.blit(unit_image, (img_x, img_y))
            else:
                
                unit_text = self.symbol_font.render(unit.get_unit_symbol(), True, Colors.BLACK)
                screen.blit(unit_text, (self.rect.x + 10, self.rect.y + 10))
            
            
            health_percent = unit.get_health() / unit.get_max_health()
            health_width = int(50 * health_percent)
            
            pygame.draw.rect(screen, Colors.RED, (self.rect.x + 5, self.rect.y + 5, 50, 8))
            pygame.draw.rect(screen, Colors.GREEN, (self.rect.x + 5, self.rect.y + 5, health_width, 8))
        
        coord_text = self.small_font.render(f"{self.coordinates.x},{self.coordinates.y}", True, Colors.WHITE)
        screen.blit(coord_text, (self.rect.x + 5, self.rect.y + 45))
        
        pygame.draw.rect(screen, Colors.GRAY, self.rect, 1)

class GameWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Стратегия - Пошаговая игра")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        
        self.image_loader = ImageLoader()
        
        
        self.game = GameController(14, 14)
        self.game.create_default_terrain()
        self.setup_game()
        
        
        self.selected_unit = None
        self.possible_moves: Set[Coordinates] = set()
        self.possible_targets: List[Unit] = []
        self.unit_has_moved = False
        
        self.cells: List[List[MapCell]] = []
        for y in range(self.game.get_map().get_height()):
            row = []
            for x in range(self.game.get_map().get_width()):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = MapCell(rect, Coordinates(x, y), self.game, self.handle_cell_click)
                row.append(cell)
            self.cells.append(row)
        
        
        self.info_panel_rect = pygame.Rect(14 * CELL_SIZE, 0, INFO_PANEL_WIDTH, WINDOW_HEIGHT)
        self.unit_panels: List[UnitInfoPanel] = []
        
        
        self.attack_button_rect = pygame.Rect(14 * CELL_SIZE + 50, 150, 150, 40)
        self.end_turn_button_rect = pygame.Rect(14 * CELL_SIZE + 50, 200, 150, 40)
        
        self.create_unit_panels()
    
    def setup_game(self):
        rnd = random.Random()
        
        
        unit_types = ["archer", "swordsman", "horseman", "catapult"]
        for unit_type in unit_types:
            while True:
                x = rnd.randint(0, 4)
                y = rnd.randint(0, 4)
                c = Coordinates(x, y)
                
                if (self.game.get_map().is_cell_passable(c) and 
                    not self.game.get_map().is_cell_occupied(c)):
                    self.game.create_unit(unit_type, self.game.get_player1(), c)
                    break
        
        
        for unit_type in unit_types:
            while True:
                x = rnd.randint(self.game.get_map().get_width() - 5, self.game.get_map().get_width() - 1)
                y = rnd.randint(self.game.get_map().get_height() - 5, self.game.get_map().get_height() - 1)
                c = Coordinates(x, y)
                
                if (self.game.get_map().is_cell_passable(c) and 
                    not self.game.get_map().is_cell_occupied(c)):
                    self.game.create_unit(unit_type, self.game.get_player2(), c)
                    break
    
    def create_unit_panels(self):
        self.unit_panels.clear()
        y_offset = 300
        for unit in self.game.get_current_player().get_alive_units():
            rect = pygame.Rect(14 * CELL_SIZE + 10, y_offset, INFO_PANEL_WIDTH - 20, 50)
            panel = UnitInfoPanel(rect, unit, self.game, self.select_unit, self.show_attack_targets)
            self.unit_panels.append(panel)
            y_offset += 60
    
    def update_unit_panels(self):
        self.create_unit_panels()
    
    def select_unit(self, unit: Unit):
        if not self.unit_has_moved:
            self.selected_unit = unit
            self.show_possible_moves(unit)
    
    def clear_highlights(self):
        for row in self.cells:
            for cell in row:
                cell.is_highlighted = False
                cell.is_attack_highlight = False
    
    def show_possible_moves(self, unit: Unit):
        self.clear_highlights()
        self.possible_moves.clear()
        
        for row in self.cells:
            for cell in row:
                if unit.can_move_to(cell.coordinates, self.game.get_map()):
                    self.possible_moves.add(cell.coordinates)
                    cell.is_highlighted = True
    
    def show_attack_targets(self):
        if self.selected_unit is None:
            return
        
        self.clear_highlights()
        self.possible_targets.clear()
        
        for unit in self.game.get_map().get_all_units():
            if (unit.owner != self.selected_unit.owner and unit.is_alive()):
                distance = self.selected_unit.get_coordinates().distance_to(unit.get_coordinates())
                if self.selected_unit.can_attack_at_distance(distance):
                    self.possible_targets.append(unit)
                    coord = unit.get_coordinates()
                    self.cells[coord.y][coord.x].is_attack_highlight = True
        
        if not self.possible_targets:
            self.show_message("Нет целей для атаки!")
    
    def handle_cell_click(self, coordinates: Coordinates):
        unit = self.game.get_map().get_unit_at(coordinates)
        current_player = self.game.get_current_player()
        
        
        if (self.selected_unit and not self.unit_has_moved and 
            coordinates in self.possible_moves):
            
            if self.game.move_unit(self.selected_unit, coordinates):
                self.unit_has_moved = True
                self.clear_highlights()
        
        
        elif self.selected_unit and self.possible_targets:
            for target in self.possible_targets:
                if target.get_coordinates() == coordinates:
                    if self.game.attack(self.selected_unit, target):
                        self.selected_unit = None
                        self.possible_targets.clear()
                        self.unit_has_moved = False
                        self.clear_highlights()
                        self.update_unit_panels()
                        
                        if self.game.is_game_over():
                            self.show_game_over()
                            return
                        
                        self.end_turn()
                    return
        
        elif (not self.unit_has_moved and unit and 
              unit.is_alive() and unit.owner == current_player):
            
            self.selected_unit = unit
            self.show_possible_moves(unit)
    
    def end_turn(self):
        self.game.switch_player()
        self.selected_unit = None
        self.possible_moves.clear()
        self.possible_targets.clear()
        self.unit_has_moved = False
        
        self.clear_highlights()
        self.update_unit_panels()
        
        if self.game.is_game_over():
            self.show_game_over()
    
    def show_game_over(self):
        winner = self.game.get_winner()
        self.show_message(f"Игра окончена!\nПобедитель: {winner.name}")
        self.running = False
    
    def show_message(self, text: str):
        
        dialog_width = 400
        dialog_height = 200
        dialog_rect = pygame.Rect(
            (WINDOW_WIDTH - dialog_width) // 2,
            (WINDOW_HEIGHT - dialog_height) // 2,
            dialog_width, dialog_height
        )
        
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        
        pygame.draw.rect(self.screen, Colors.WHITE, dialog_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, dialog_rect, 2)
        
        
        lines = text.split('\n')
        y_offset = dialog_rect.y + 50
        for line in lines:
            text_surf = self.font.render(line, True, Colors.BLACK)
            text_rect = text_surf.get_rect(center=(dialog_rect.centerx, y_offset))
            self.screen.blit(text_surf, text_rect)
            y_offset += 30
        
        
        ok_rect = pygame.Rect(dialog_rect.centerx - 50, dialog_rect.bottom - 60, 100, 30)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, ok_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, ok_rect, 1)
        ok_text = self.font.render("OK", True, Colors.BLACK)
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        self.screen.blit(ok_text, ok_text_rect)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if ok_rect.collidepoint(event.pos):
                        waiting = False
    
    def draw_info_panel(self):
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, self.info_panel_rect)
        pygame.draw.line(self.screen, Colors.GRAY, 
                        (self.info_panel_rect.left, 0), 
                        (self.info_panel_rect.left, WINDOW_HEIGHT), 2)
        
        
        turn_text = self.title_font.render(f"Ход: {self.game.get_current_player().name}", 
                                          True, Colors.BLACK)
        self.screen.blit(turn_text, (self.info_panel_rect.x + 20, 20))
        
        
        if self.selected_unit:
            selected_text = self.font.render(
                f"Выбран: {self.selected_unit.get_type()} (❤️ {self.selected_unit.get_health()})",
                True, Colors.BLACK
            )
            self.screen.blit(selected_text, (self.info_panel_rect.x + 20, 70))
        else:
            selected_text = self.font.render("Юнит не выбран", True, Colors.BLACK)
            self.screen.blit(selected_text, (self.info_panel_rect.x + 20, 70))
        
        
        attack_color = Colors.GREEN if self.selected_unit else Colors.GRAY
        pygame.draw.rect(self.screen, attack_color, self.attack_button_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, self.attack_button_rect, 1)
        attack_text = self.font.render("Атаковать", True, Colors.BLACK)
        attack_text_rect = attack_text.get_rect(center=self.attack_button_rect.center)
        self.screen.blit(attack_text, attack_text_rect)
        
        
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, self.end_turn_button_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, self.end_turn_button_rect, 1)
        end_text = self.font.render("Закончить ход", True, Colors.BLACK)
        end_text_rect = end_text.get_rect(center=self.end_turn_button_rect.center)
        self.screen.blit(end_text, end_text_rect)
        
        
        units_title = self.font.render("Юниты:", True, Colors.BLACK)
        self.screen.blit(units_title, (self.info_panel_rect.x + 20, 270))
        
        
        for panel in self.unit_panels:
            panel.draw(self.screen)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                
                if self.attack_button_rect.collidepoint(pos) and self.selected_unit:
                    self.show_attack_targets()
                
                elif self.end_turn_button_rect.collidepoint(pos):
                    self.end_turn()
                
                
                for panel in self.unit_panels:
                    panel.handle_click(pos)
                
                
                for row in self.cells:
                    for cell in row:
                        cell.handle_click(pos)
    
    def draw(self):
        self.screen.fill(Colors.WHITE)
        
        for row in self.cells:
            for cell in row:
                cell.draw(self.screen)
        

        self.draw_info_panel()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

class StrategyGame:
    @staticmethod
    def main():
        game = GameWindow()
        game.run()

if __name__ == "__main__":
    StrategyGame.main()
