#from main.building_blocks.pauli.Pauli import Pauli
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from numerics.idling_experiment import IdlingExperiment
from main.compiling.noise.models.CodeCapacityBitFlipNoise \
    import CodeCapacityBitFlipNoise


rep_exp = IdlingExperiment('RepetitionCode', 3,CodeCapacityBitFlipNoise(0.2))#,measurement=0.1))
ler = rep_exp.calculate_ler(100)
print(ler,'ler')

exp = IdlingExperiment('RotatedSurfaceCode', 5, CodeCapacityBitFlipNoise(0.2))