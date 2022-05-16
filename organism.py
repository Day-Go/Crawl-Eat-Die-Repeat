import math
import uuid
import pymunk
import random

from dataclasses import dataclass
from appendages import Head, Limb

# "a4b923 de631f cc31a4 ab53e17"
class Organism():
    def __init__(self, genome="") -> None:
        
        self.genome = genome

        self.body = Body(genome, uuid.uuid4())



# gene length definitely need to be longer to encode
# joint type and position encoding
@dataclass        
class Body():
    genome: str
    id: str
    
    def __post_init__(self):
        self.head = Head(str(uuid.uuid4()))

        # at the end of the limb generation we terminate the tree branches
        # with None -> indicating there are no more parts to add
        self.structure = {
            self.head.id: {
                "obj": self.head,
                "parent": None,
                "children": []
            }
        }
 
        self.body_parts = []
        self.genes = self.genome.split(" ")

        self.generate_limbs()
        self.design_body()


    def generate_limbs(self) -> None:
        for gene in self.genes:
            limb = Limb(gene, str(uuid.uuid4()))
            self.body_parts.append(limb)

    def add_part_to_structure(self, part, joint, endpoints, parent_id) -> None:
        self.structure.update({
            part.id: {
                "obj": part,
                "joint": joint,
                "endpoints": endpoints,
                "parent": parent_id,
                "children": []
            }
        })

    def add_torso(self) -> None:
        part = self.body_parts[0]
        part.matter.position = self.head.matter.position
        
        # list of tuples
        endpoints = [
            (part.matter.position[0] + part.end_1[0],
            part.matter.position[1] + part.end_1[1]),
            (part.matter.position[0] + part.end_2[0],
            part.matter.position[1] + part.end_2[1])
        ]

        joint = pymunk.constraints.PivotJoint(
            part.matter, 
            self.head.matter, 
            self.head.matter.position
        )

        joint.collide_bodies = False

        self.add_part_to_structure(part, joint, endpoints, self.head.id)

        self.structure[self.head.id]["children"].append(part.id)
    
    def add_limb(self, parent_id, part):
        # parent_id = random.choice(list(self.structure))
        parent = self.structure[parent_id]["obj"]       

        # very bad way of checking if the parent object is the torso
        # hesitant to add a new field to struct but might have to 
        grandparent_id = self.structure[parent_id]["parent"]
        if isinstance(self.structure[grandparent_id]["obj"], Head): 
            endpoint_idx = random.randint(0,1)
        else:
            endpoint_idx = 1

        position = self.structure[parent_id]["endpoints"][endpoint_idx]

        # print(position)
        part.matter.position = (position[0] + part.v_x/2,
                                position[1] + part.v_y/2)

        endpoints = [
            (part.matter.position[0] - part.v_x/2,
                part.matter.position[1] - part.v_y/2),
            (part.matter.position[0] + part.v_x/2,
                part.matter.position[1] + part.v_y/2)
        ]

        joint = pymunk.constraints.PivotJoint(
            part.matter, 
            parent.matter, 
            position
        )

        joint.collide_bodies = False

        self.add_part_to_structure(part, joint, endpoints, parent_id)

        self.structure[parent_id]["children"].append(part.id)


    def choose_parent(self) -> None:
        parent_id = random.choice(list(self.structure))

        if len(self.structure[parent_id]["children"]) >= 2:
            parent_id = self.choose_parent()
        
        return parent_id    

    """
    how can we implicitly encode limb position into the genome
    the position of the limb is important. A limb that is usefull
    near the head will not be useful at the extremities.

    last bit indicates hand or no hand.
    if hand we terminate the branch with None 
    """
    def design_body(self) -> None:
        self.add_torso()
        for part in self.body_parts[1:]:
            parent_id = self.choose_parent()

            if isinstance(self.structure[parent_id]["obj"], Head):
                self.add_torso()
            else:
                self.add_limb(parent_id, part)

        

    def construct_body(self):
        pass


