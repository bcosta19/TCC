import optframe
from optframe.components import Move
import random
import numpy as np

"""
Representação de uma solução do problema de alocação de salas
"""
class SolutionClassroom(object):
    def __init__(self):
        self.assignment : list[int] = []  # assignment[i] = sala da turma i

    def __str__(self):
        return f"SolutionClassroom(assignment={self.assignment})"


"""
Definição do problema de alocação de salas
"""
class ClassroomAllocation(object):
    def __init__(self):
        self.engine = optframe.Engine()
        self.num_classes : int = 0
        self.num_rooms : int = 0
        self.class_size : list[int] = []  # tamanho das turmas
        self.class_time : list[int] = []  # horário da turma (ex: 1,2,3)
        self.room_capacity : list[int] = []  # capacidade das salas
        self.room_available_time : list[list[int]] = []  # disponibilidade por sala

    """
        Carregar dados do problema
        Formato do arquivo:
        num_classes num_rooms
        class_sizes (linha com n valores)
        class_times (linha com n valores)
        room_capacities (linha com m valores)
        linhas seguintes: horários disponíveis de cada sala
    """
    def load(self, filename: str):
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.num_classes, self.num_rooms = map(int, lines[0].split())
            self.class_size = list(map(int, lines[1].split()))
            self.class_time = list(map(int, lines[2].split()))
            self.room_capacity = list(map(int, lines[3].split()))

            self.room_available_time = []
            for i in range(self.num_rooms):
                times = list(map(int, lines[4+i].split()))
                self.room_available_time.append(times)

    def __str__(self):
        return (f"ClassroomAllocation(classes={self.num_classes}, rooms={self.num_rooms}, "
                f"sizes={self.class_size}, times={self.class_time}, capacity={self.room_capacity}, "
                f"availability={self.room_available_time})")

    """
        Gera uma solução aleatória
    """
    @staticmethod
    def generateSolution(problem: 'ClassroomAllocation') -> SolutionClassroom:
        sol = SolutionClassroom()
        sol.assignment = [random.randint(0, problem.num_rooms-1) for _ in range(problem.num_classes)]
        return sol

    """
        Avaliar solução
        Penalizações:
        - Turma alocada em sala sem horário → -1000
        - Sala com capacidade < turma → -10 * excesso
        - Conflito de turmas no mesmo horário/sala → -500 por conflito
    """
    @staticmethod
    def maximize(p: 'ClassroomAllocation', sol: SolutionClassroom) -> float:
        score = 0.0
        conflicts = 0

        for i in range(p.num_classes):
            sala = sol.assignment[i]
            turma_size = p.class_size[i]
            turma_time = p.class_time[i]

            # penaliza se sala não suporta
            if turma_size > p.room_capacity[sala]:
                score -= 10.0 * (turma_size - p.room_capacity[sala])

            # penaliza se horário não está disponível
            if turma_time not in p.room_available_time[sala]:
                score -= 1000.0

        # verificar conflitos de horário na mesma sala
        for r in range(p.num_rooms):
            classes_in_room = [i for i in range(p.num_classes) if sol.assignment[i] == r]
            times_seen = {}
            for c in classes_in_room:
                t = p.class_time[c]
                if t in times_seen:
                    conflicts += 1
                else:
                    times_seen[t] = True
        score -= 500.0 * conflicts

        return score


"""
Um movimento que muda a sala de uma turma
"""
class MoveReassign(Move):
    def __init__(self, class_id: int, new_room: int):
        self.class_id = class_id
        self.new_room = new_room

    def apply(self, problemCtx: ClassroomAllocation, sol: SolutionClassroom) -> 'MoveReassign':
        old_room = sol.assignment[self.class_id]
        sol.assignment[self.class_id] = self.new_room
        return MoveReassign(self.class_id, old_room)  # movimento reverso

    def canBeApplied(self, problemCtx: ClassroomAllocation, sol: SolutionClassroom) -> bool:
        return True


class NSReassign(object):
    @staticmethod
    def randomMove(p: ClassroomAllocation, sol: SolutionClassroom) -> MoveReassign:
        c = random.randint(0, p.num_classes-1)
        new_room = random.randint(0, p.num_rooms-1)
        return MoveReassign(c, new_room)


# ---------------------------
# Execução
# ---------------------------

problem = ClassroomAllocation()
problem.load("classroom-example.txt")

problem.engine.setup(problem)

# Registrar NS
problem.engine.add_ns_class(problem, NSReassign)

fev = problem.engine.get_evaluator(0)
fc = problem.engine.get_constructive(0)

sol = problem.engine.fconstructive_gensolution(fc)
print("Solução inicial:", sol)

z = problem.engine.fevaluator_evaluate(fev, False, sol)
print("Valor da solução inicial:", z)

