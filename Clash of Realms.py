import threading
import time
import random
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict

# Custom Exceptions for MMO Game
class InvalidActionError(Exception):
    pass

class NotEnoughManaError(Exception):
    pass

class OutOfBoundsError(Exception):
    pass

# Decorator for logging player actions
def log_action(func):
    def wrapper(*args, **kwargs):
        player = args[0]
        action_name = func.__name__.replace('_', ' ').capitalize()
        print(f"[LOG] {player.name} is attempting to {action_name}")
        result = func(*args, **kwargs)
        return result
    return wrapper

# Abstract Base Class for Players
class Player(ABC):
    def __init__(self, name, health, mana):
        self.name = name
        self.health = health
        self.mana = mana
        self.inventory = []
        self.location = (0, 0)  # x, y in the world grid
        self.level = 1
        self.experience = 0
        self.lock = threading.Lock()

    @abstractmethod
    def attack(self, target):
        pass

    @abstractmethod
    def special_ability(self, target):
        pass

    def move(self, dx, dy):
        with self.lock:
            new_location = (self.location[0] + dx, self.location[1] + dy)
            print(f"{self.name} moves from {self.location} to {new_location}")
            self.location = new_location

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} takes {damage} damage. Remaining health: {self.health}")
        if self.health <= 0:
            print(f"{self.name} has been defeated!")

    def heal(self, amount):
        self.health += amount
        print(f"{self.name} heals {amount} points. Current health: {self.health}")

    def gain_experience(self, exp):
        self.experience += exp
        print(f"{self.name} gained {exp} experience points. Total experience: {self.experience}")
        if self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.health += 50
        self.mana += 20
        self.experience = 0
        print(f"{self.name} has leveled up! Now at level {self.level} with {self.health} health and {self.mana} mana.")

    def __str__(self):
        return f"Player({self.name}, HP: {self.health}, MP: {self.mana}, Location: {self.location})"

# Warrior Class
class Warrior(Player):
    def __init__(self, name):
        super().__init__(name, health=200, mana=50)

    @log_action
    def attack(self, target):
        damage = random.randint(15, 30)
        print(f"{self.name} strikes {target.name} for {damage} damage!")
        target.take_damage(damage)

    @log_action
    def special_ability(self, target):
        if self.mana < 20:
            raise NotEnoughManaError(f"{self.name} doesn't have enough mana to use special ability!")
        self.mana -= 20
        damage = random.randint(30, 50)
        print(f"{self.name} uses 'Power Strike' on {target.name} for {damage} damage!")
        target.take_damage(damage)

# Mage Class
class Mage(Player):
    def __init__(self, name):
        super().__init__(name, health=120, mana=150)

    @log_action
    def attack(self, target):
        damage = random.randint(10, 20)
        print(f"{self.name} casts a fireball at {target.name}, dealing {damage} damage!")
        target.take_damage(damage)

    @log_action
    def special_ability(self, target):
        if self.mana < 50:
            raise NotEnoughManaError(f"{self.name} doesn't have enough mana to cast special ability!")
        self.mana -= 50
        damage = random.randint(40, 70)
        print(f"{self.name} casts 'Blizzard' on {target.name}, dealing {damage} damage!")
        target.take_damage(damage)

# Rogue Class
class Rogue(Player):
    def __init__(self, name):
        super().__init__(name, health=150, mana=70)

    @log_action
    def attack(self, target):
        damage = random.randint(20, 25)
        print(f"{self.name} stabs {target.name} with a dagger, dealing {damage} damage!")
        target.take_damage(damage)

    @log_action
    def special_ability(self, target):
        if self.mana < 30:
            raise NotEnoughManaError(f"{self.name} doesn't have enough mana to use special ability!")
        self.mana -= 30
        damage = random.randint(35, 60)
        print(f"{self.name} uses 'Backstab' on {target.name}, dealing {damage} damage!")
        target.take_damage(damage)

# World class that stores all players and handles movement/combat
class World:
    def __init__(self, size=10):
        self.size = size
        self.players = []
        self.npcs = []
        self.quests = []

    def add_player(self, player):
        self.players.append(player)
        print(f"{player.name} has joined the world at location {player.location}.")

    def move_player(self, player, dx, dy):
        new_x, new_y = player.location[0] + dx, player.location[1] + dy
        if not (0 <= new_x < self.size and 0 <= new_y < self.size):
            raise OutOfBoundsError(f"{player.name} tried to move out of bounds!")
        player.move(dx, dy)

    def start_combat(self, player1, player2):
        print(f"Combat initiated between {player1.name} and {player2.name}!")
        while player1.health > 0 and player2.health > 0:
            player1.attack(player2)
            if player2.health <= 0:
                print(f"{player2.name} has been defeated by {player1.name}!")
                player1.gain_experience(50)
                return
            player2.attack(player1)
            if player1.health <= 0:
                print(f"{player1.name} has been defeated by {player2.name}!")
                player2.gain_experience(50)

# Inventory System
class InventoryItem:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

    def __str__(self):
        return f"Item({self.name}, Effect: {self.effect})"

class Inventory:
    def __init__(self):
        self.items = defaultdict(int)

    def add_item(self, item, quantity=1):
        self.items[item.name] += quantity
        print(f"Added {quantity} of {item.name} to inventory.")

    def use_item(self, item_name, player):
        if self.items[item_name] <= 0:
            print(f"{item_name} is not available in inventory.")
            return
        self.items[item_name] -= 1
        print(f"{player.name} used {item_name}. Effect: {player.heal(20)}")

    def __str__(self):
        return f"Inventory: {dict(self.items)}"

# NPC Class
class NPC:
    def __init__(self, name, dialogue):
        self.name = name
        self.dialogue = dialogue

    def interact(self, player):
        print(f"{self.name}: {self.dialogue}")

# Quests
class Quest:
    def __init__(self, title, reward, task):
        self.title = title
        self.reward = reward
        self.task = task
        self.completed = False

    def complete(self, player):
        print(f"Quest '{self.title}' completed!")
        player.gain_experience(self.reward)
        self.completed = True

# Simulated MMO Server with threads for each player
class MMOServer:
    def __init__(self):
        self.players = []
        self.world = World()

    def add_player(self, player):
        self.players.append(player)
        self.world.add_player(player)
        threading.Thread(target=self.handle_player, args=(player,)).start()

    def handle_player(self, player):
        print(f"Handling player {player.name} on a new thread.")
        while player.health > 0:
            time.sleep(random.randint(1, 3))  # Simulate server processing delays
            action = random.choice(["move", "combat", "quest", "inventory"])
            if action == "move":
                try:
                    self.world.move_player(player, random.randint(-1, 1), random.randint(-1, 1))
                except OutOfBoundsError as e:
                    print(e)
            elif action == "combat":
                if len(self.world.players) > 1:
                    opponent = random.choice([p for p in self.world.players if p != player])
                    self.world.start_combat(player, opponent)
            elif action == "quest":
                quest = Quest("Find the Lost Sword", 100, "Retrieve the ancient sword from the dungeon.")
                player.gain_experience(quest.reward)
            elif action == "inventory":
                potion = InventoryItem("Health Potion", "Heals 20 HP")
                player.inventory.append(potion)
                print(f"{player.name} found a Health Potion!")

# Test Simulation
if __name__ == "__main__":
    server = MMOServer()
    
    # Create players
    player1 = Warrior("Thor")
    player2 = Mage("Merlin")
    player3 = Rogue("Shadow")
    
    # Add players to server
    server.add_player(player1)
    server.add_player(player2)
    server.add_player(player3)

    # Let the game run for a bit
    time.sleep(20)
    print("\nGame Over. Final Stats:")
    for player in server.players:
        print(player)
