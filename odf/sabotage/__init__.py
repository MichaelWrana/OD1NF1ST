from odf.sabotage.Attack_1 import *
from odf.sabotage.Attack_2 import *
from odf.sabotage.Attack_3 import *
from odf.sabotage.Attack_4 import *
from odf.sabotage.Attack_5 import *
from odf.sabotage.Attack_6 import *
from odf.sabotage.Attack_7 import *
from odf.sabotage.Attack_8 import *
from odf.sabotage.Attack_9 import *
from odf.sabotage.Attack_10 import *
from odf.utils import all_subclasses

all_attacks = all_subclasses(Sabotage, leaves_only=True)
