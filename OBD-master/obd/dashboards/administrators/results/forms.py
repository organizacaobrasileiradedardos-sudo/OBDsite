from decouple import config
from django import forms


import re

# Class form for player to register results from match
from obd.dashboards.administrators.fixtures.models import Fixture





class ResultForm(forms.Form):
    # Subforms for general data/info
    division = forms.IntegerField(label='Liga/Divisão', required=False)
    match = forms.IntegerField(label='#ID Partida', required=False)
    player1 = forms.IntegerField(label='Jogador(a) 1', required=False)
    player2 = forms.IntegerField(label='Joagdor(a) 2', required=False)
    comment = forms.CharField(label='Comentários', required=False, max_length=250)

    # Subforms for Player 01
    sets_p1 = forms.IntegerField(label='Sets Jogador 1', required=False)
    legs_p1 = forms.IntegerField(label='Legs Jogador 1', required=False)
    highest_out_p1 = forms.IntegerField(label='Melhor Fechada Jogador 1', required=False)
    best_leg_p1 = forms.IntegerField(label='Melhor Leg Jogador 1', required=False)
    ton_p1 = forms.IntegerField(label='100+ JOgador 1', required=False)
    ton40_p1 = forms.IntegerField(label='140+ JOgador 1', required=False)
    ton70_p1 = forms.IntegerField(label='170+ JOgador 1', required=False)
    ton80_p1 = forms.IntegerField(label='140+ JOgador 1', required=False)
    average_p1 = forms.FloatField(label='Média Jogador 1', required=False)

    # Subforms for Player 02
    sets_p2 = forms.IntegerField(label='Sets Jogador 2', required=False)
    legs_p2 = forms.IntegerField(label='Legs Jogador 2', required=False)
    highest_out_p2 = forms.IntegerField(label='Melhor Fechada Jogador 2', required=False)
    best_leg_p2 = forms.IntegerField(label='Melhor Leg Jogador 2', required=False)
    ton_p2 = forms.IntegerField(label='100+ JOgador 2', required=False)
    ton40_p2 = forms.IntegerField(label='140+ JOgador 2', required=False)
    ton70_p2 = forms.IntegerField(label='170+ JOgador 2', required=False)
    ton80_p2 = forms.IntegerField(label='140+ JOgador 2', required=False)
    average_p2 = forms.FloatField(label='Média Jogador 2', required=False)

    photo = forms.ImageField(label='Anexo', required=False)



    def clean_sets_p2(self):
        p2_sets = self.cleaned_data['sets_p2']
        p1_sets = self.cleaned_data['sets_p1']
        total = p1_sets + p2_sets
        game = Fixture.objects.get(id=self.cleaned_data['match'])
        division = game.division.formation


        if total == 0:
            return self.cleaned_data['sets_p2']

        if division == 1:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueAplayoffs:
                return self.cleaned_data['sets_p2']

            max_a = game.division.league.enviroment.leagueAMaxSet

            if max_a % 2 == 1:
                min_a = (max_a//2)+1
            else:
                min_a = max_a//2

            if (total > max_a) or (total < min_a):
                if max_a == 1:
                    raise forms.ValidationError(f'De acordo com as regras OBD para divisão A, o total de SETS jogados deve ser igual a 1.')
                raise forms.ValidationError(f'De acordo com as regras OBD para divisão A, o total de SETS jogados deve estar entre {min_a} e {max_a}.')
            else:
                return self.cleaned_data['sets_p2']

        if division == 2:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueBplayoffs:
                return self.cleaned_data['sets_p2']

            max_b = game.division.league.enviroment.leagueBMaxSet

            if max_b % 2 == 1:
                min_b = (max_b//2) + 1
            else:
                min_b = max_b//2

            if (total > max_b) or (total < min_b):
                if max_b == 1:
                    raise forms.ValidationError(f'De acordo com as regras OBD para divisão B, o total de SETS jogados deve ser igual a 1.')
                raise forms.ValidationError(f'De acordo com as regras OBD para divisão B, o total de SETS jogados deve estar entre {min_b} e {max_b}.')
            else:
                return self.cleaned_data['sets_p2']

        if division == 3:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueCplayoffs:
                return self.cleaned_data['sets_p2']

            max_c = game.division.league.enviroment.leagueCMaxSet

            if max_c % 2 == 1:
                min_c = (max_c//2) + 1
            else:
                min_c = max_c//2

            if (total > max_c) or (total < min_c):
                if max_c == 1:
                    raise forms.ValidationError(f'De acordo com as regras OBD para divisão C, o total de SETS jogados deve ser igual a 1.')
                raise forms.ValidationError(f'De acordo com as regras OBD para divisão C, o total de SETS jogados deve estar entre {min_c} e {max_c}.')
            else:
                return self.cleaned_data['sets_p2']

        if division > 3:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueOthersplayoffs:
                return self.cleaned_data['sets_p2']

            max_d = game.division.league.enviroment.leagueCMaxSet

            if max_d % 2 == 1:
                min_d = (max_d // 2) + 1
            else:
                min_d = max_d // 2

            if (total > max_d) or (total < min_d):
                if max_d == 1:
                    raise forms.ValidationError(f'De acordo com as regras OBD para sua divisão, o total de SETS jogados deve ser igual a 1.')
                raise forms.ValidationError(f'De acordo com as regras OBD para esta divisão, o total de SETS jogados deve estar entre {min_d} e {max_d}.')
            else:
                return self.cleaned_data['sets_p2']


    def clean_legs_p2(self):
        p2_legs = self.cleaned_data['legs_p2']
        p1_legs = self.cleaned_data['legs_p1']
        game = Fixture.objects.get(id=self.cleaned_data['match'])
        division = game.division.formation

        if division == 1:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueAplayoffs:
                return self.cleaned_data['legs_p2']

            max_legs = game.division.league.enviroment.leagueAFirstTo
            min_legs = game.division.league.enviroment.leagueABestof
            if min_legs % 2 == 0:
                min_legs = int(min_legs / 2)
            else:
                min_legs = int((min_legs + 1) / 2)

            if (p2_legs + p1_legs) > min_legs*2:
                raise forms.ValidationError(f'O número de LEGS total excedeu o máximo permitido de acordo com a regra "Melhor de {min_legs*2}" legs.')

            if (p2_legs > max_legs) or (p1_legs > max_legs):
                raise forms.ValidationError(f'De acordo com as regras OBD, "{max_legs}" é o número máximo de LEGS para a divisão A.')
            else:
                if ((p2_legs < min_legs) and (p1_legs < max_legs)) or ((p1_legs < min_legs) and (p2_legs < max_legs)):
                    raise forms.ValidationError(f'Com base nos LEGS informados e regra OBD de "Melhor de {min_legs*2}", não é possível definir o resultado da partida.')
                else:
                    return self.cleaned_data['legs_p2']

        if division == 2:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueBplayoffs:
                return self.cleaned_data['legs_p2']

            max_legs = game.division.league.enviroment.leagueBFirstTo
            min_legs = game.division.league.enviroment.leagueBBestof
            if min_legs % 2 == 0:
                min_legs = int(min_legs / 2)
            else:
                min_legs = int((min_legs + 1) / 2)

            if (p2_legs + p1_legs) > min_legs*2:
                raise forms.ValidationError(f'O número de LEGS total excedeu o máximo permitido de acordo com a regra "Melhor de {min_legs*2}" legs.')

            if (p2_legs > max_legs) or (p1_legs > max_legs):
                raise forms.ValidationError(f'De acordo com as regras OBD, "{max_legs}" é o número máximo de LEGS para a divisão B.')
            else:
                if ((p2_legs < min_legs) and (p1_legs < max_legs)) or ((p1_legs < min_legs) and (p2_legs < max_legs)):
                    raise forms.ValidationError(f'Com base nos LEGS informados e regra OBD de "Melhor de {min_legs * 2}", não é possível definir o resultado da partida.')
                else:
                    return self.cleaned_data['legs_p2']


        if division == 3:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueCplayoffs:
                return self.cleaned_data['legs_p2']

            max_legs = game.division.league.enviroment.leagueCFirstTo
            min_legs = game.division.league.enviroment.leagueCBestof
            if min_legs % 2 == 0:
                min_legs = int(min_legs / 2)
            else:
                min_legs = int((min_legs + 1) / 2)

            if (p2_legs + p1_legs) > min_legs*2:
                raise forms.ValidationError(f'O número de LEGS total excedeu o máximo permitido de acordo com a regra "Melhor de {min_legs*2}" legs.')

            if (p2_legs > max_legs) or (p1_legs > max_legs):
                raise forms.ValidationError(f'De acordo com as regras OBD, "{max_legs}" é o número máximo de LEGS para a divisão C.')
            else:
                if ((p2_legs < min_legs) and (p1_legs < max_legs)) or ((p1_legs < min_legs) and (p2_legs < max_legs)):
                    raise forms.ValidationError(f'Com base nos LEGS informados e regra OBD de "Melhor de {min_legs * 2}", não é possível definir o resultado da partida.')
                else:
                    return self.cleaned_data['legs_p2']


        if division > 3:

            # If division has playoffs, may return SETS without analyse it.
            if game.division.league.enviroment.leagueOthersplayoffs:
                return self.cleaned_data['legs_p2']

            max_legs = game.division.league.enviroment.leagueOthersFirstTo
            min_legs = game.division.league.enviroment.leagueOthersBestof
            if min_legs % 2 == 0:
                min_legs = int(min_legs / 2)
            else:
                min_legs = int((min_legs + 1) / 2)

            if (p2_legs + p1_legs) > min_legs*2:
                raise forms.ValidationError(f'O número de LEGS total excedeu o máximo permitido de acordo com a regra "Melhor de {min_legs*2}" legs.')

            if (p2_legs > max_legs) or (p1_legs > max_legs):
                raise forms.ValidationError(f'De acordo com as regras OBD, "{max_legs}" é o número máximo de LEGS para a sua divisão.')
            else:
                if ((p2_legs < min_legs) and (p1_legs < max_legs)) or ((p1_legs < min_legs) and (p2_legs < max_legs)):
                    raise forms.ValidationError(f'Com base nos LEGS informados e regra OBD de "Melhor de {min_legs * 2}", não é possível definir o resultado da partida.')
                else:
                    return self.cleaned_data['legs_p2']


    def clean_average_p2(self):
        avg_p2 = self.cleaned_data['average_p2']
        avg_p1 = self.cleaned_data['average_p1']

        if (avg_p2 > 167) or (avg_p1 > 167):
            raise forms.ValidationError(f'Para o 501 (SD) a média máxima calculável é de 167.')
        else:
            return self.cleaned_data['average_p2']


    def clean_highest_out_p2(self):
        out_p2 = self.cleaned_data['highest_out_p2']
        out_p1 = self.cleaned_data['highest_out_p1']

        possibilities = (1, 159, 162, 163, 165, 166, 168, 169)

        if ((out_p2 > 170) or (out_p1 > 170) or (out_p2 in possibilities) or (out_p1 in possibilities)):
            raise forms.ValidationError(f'A fechada não pode ser maior que 170 ou igual a um dos valores: {possibilities}.')
        else:
            return self.cleaned_data['highest_out_p2']


    def clean_best_leg_p2(self):
        best_p2 = self.cleaned_data['best_leg_p2']
        best_p1 = self.cleaned_data['best_leg_p1']

        if (best_p2 < 9 and best_p2 != 0) or (best_p1 < 9 and best_p1 != 0):
            raise forms.ValidationError(f'Para o 501 (SD), "9 dardos" é o menor número possível para vencer um leg.')
        else:
            return self.cleaned_data['best_leg_p2']

