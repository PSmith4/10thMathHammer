from nicegui import ui
from weapon import Weapon
ui.label('Hello NiceGUI!')


enahm_toughness= 4

bolter1=Weapon( ['2','3','4','0','1',''])
bolter2=Weapon( ['2','3','4','0','1','sustained hit 1'])
bolter3=Weapon( ['2','3','4','0','1','lethal hit'])
bolter4=Weapon( ['2','3','4','0','1','lethal hit sustained hit 1'])


print("____Normal____")
hits, crits= bolter1.get_hits()
# print("asdf", hits, crits)
bolter1.get_wounds(hits, crits, enahm_toughness)

print("____Sus____")
hits, crits=bolter2.get_hits()
bolter2.get_wounds(hits, crits,enahm_toughness)

print("____lethal____")
hits, crits=bolter3.get_hits()
bolter3.get_wounds(hits, crits,enahm_toughness)


print("____both____")
hits, crits=bolter4.get_hits()
bolter4.get_wounds(hits, crits,enahm_toughness)

# ui.run()

