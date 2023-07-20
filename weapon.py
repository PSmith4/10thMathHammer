

import numpy as np
np.set_printoptions(linewidth=np.inf)

def fact(end):
    fact=1.0
    for i in range(2, end+1):
        fact = fact * i
    return fact

def fact_array(end):
    fact=1.0
    out=[1]
    for i in range(1, end+1):
        fact = fact * i
        out.append(fact)
    return np.array(out)
 
def re_roll(prob, swings, prob_array):
    hits=np.zeros( swings)
    for i in range(swings):
        fails=swings-1-i
        up= np.linspace(0.0,fails,fails+1, endpoint=True)
        fa=fact_array(fails)
        hits[i:i+fails+1] = hits[i:i+fails+1]  +  prob_array[i] *  (1-prob)**(np.flip(up))* prob**(up)* fact(fails)/fa/np.flip(fa)
    return hits
    
def re_roll_1s(hit_prob, crit_fail, swings, prob_array):
    hits=np.zeros( swings)
    for i in range(swings):
        fails=swings-1-i
        # print("fails",fails, hits[i])
        up= np.linspace(0.0,fails,fails+1, endpoint=True)
        fa=fact_array(fails)
                
        ones= (1-crit_fail)**(np.flip(up))* crit_fail**(up)* fact(fails)/fa/np.flip(fa) * prob_array[i]
        for j in range(fails+1):
            up= np.linspace(0.0,j,j+1, endpoint=True)
            fa=fact_array(j)
            # print(j, up, ones[j])
            # print(ones[j] *  (1-hit_prob)**(np.flip(up))* hit_prob**(up)* fact(j)/fa/np.flip(fa))
            hits[i:j+i+1] = hits[i:j+i+1]  +  ones[j] *  (1-hit_prob)**(np.flip(up))* hit_prob**(up)* fact(j)/fa/np.flip(fa)
        # print("rr1",hits2)
        return hits

        
class Weapon():
    def __init__(self, string):
        self.swings= string[0]
        
        self.to_hit= float(string[1])
        self.strength=float(string[2])
        self.AP=float(string[3])
        self.dmg=float(string[4])
        
        special=string[5]
        
        def extract(name):
            if name in special:
                temp=special.split(name)[1]
                for c in temp:
                    if c.isdigit():
                        return (True, int(c)) 
            
            return (False, 0)
        
        #hit things
        self.sustained_hit=extract("sustained hit")
        self.lethal_hit="lethal hit" in special
        
        # self.hits_reRoll=None
        # if "reroll hits 1s" in special:
            # self.hits_reRoll_1=True
        # elif "reroll hits all" in special:
            # self.hits_reRoll_all=True
            
            
        #number of hit things
        self.torrent="torrent" in special
        self.blast= "blast" in special
        
        #wound things
        self.anti_inf=extract("anti inf")
        self.anti_vehicle=extract("anti vehicle")
        self.anti_monster=extract("anti monster")
        self.devastating_wound="devastating wound" in special
        self.twin_linked="twin-linked" in special
        # self.wound_reRoll_oness= "reroll hits 1s" in special
        # self.wound_reRoll_all=  "reroll hits all" in special
        
        self.heavy="heavy" in special
        self.rapid_fire=extract("rapid fire")
        self.lance="lance" in special
        self.melta="melta" in special
        self.indirect = "indirect fire" in special
        self.two_profiles = any( [self.heavy, self.rapid_fire[0], self.lance , self.melta,self.indirect,self.blast])
        # print(self.two_profiles,"__",self.heavy, self.rapid_fire[0], self.lance , self.melta,self.indirect,self.blast)
        if any( [  self.lance,  self.melta, self.devastating_wound, self.anti_monster[0], self.anti_vehicle[0], self.anti_inf[0]] ):
            print("one of your special weapon types is not implemented yet")
            assert False
            
        self.auto_wound=0
        # print(self.lethal_hit, self.sustained_hit[0])
    
    def get_hits(self,  re_roll=False, re_roll_1s=False, crit=6):
        
        if not isinstance(self.swings, int) and not self.swings.isnumeric():
            self.swings= self.swings.split("+")
            self.swings[0]= int(self.swings[0].replace('D'))
            print("non numeric swing", self.swings)
            
            prob= 1.0/self.swings[0]
            
            swings= np.linspace(1, self.swings[0], self.swings[0])+self.swings[1]
            print("->", swings)
            
            hits=np.zerios(self.swings[0]+1)
            for swing in swings:
                self.swings=swing
                hits[:swing+1] = out[:swing+1] + self.get_hits(re_roll, re_roll_1s, crit) * prob 
            assert np.sum(hits)==1.0
            return hits ,None
            
        else:
            self.swings=int(self.swings)
        
        if self.torrent:
            out= np.zerios(self.swings+1)
            out[-1]=1
            return out
            
        if self.two_profiles:
            self.two_profiles=False
            out= [self.get_hits( re_roll, re_roll_1s,crit)]
            
            if self.heavy:
                temp=self.to_hit
                self.to_hit= max(self.to_hit-1, 2)
                out.append( self.get_hits(re_roll, re_roll_1s,crit))
                self.to_hit=temp
            elif self.rapid_fire[0]:
                self.swings+=self.rapid_fire[1]
                out.append( self.get_hits(re_roll, re_roll_1s,crit))
                self.swings-=self.rapid_fire[1]
            elif self.indirect:
                temp=self.to_hit
                self.to_hit= min(self.to_hit+1, 6)
                out.append( self.get_hits(re_roll, re_roll_1s,crit))
                self.to_hit=temp
            elif self.blast:
                self.swings+=1
                out.append( self.get_hits(re_roll, re_roll_1s,crit))
                self.swings+=1
                out.append( self.get_hits(re_roll, re_roll_1s,crit))
                
                self.swings-=2
            
            else:
                out.append(out[0])
            self.two_profiles=True
            assert False
            return out
            
            
            
        
        up= np.linspace(0.0,self.swings,self.swings+1, endpoint=True)
        down=np.flip(up)   
        
        
        hit_prob= (7-self.to_hit)/6.0
        # print(hit_prob)
        
        fa=fact_array(self.swings)
        # print(fact(self.swings)/fa/np.flip(fa))
        hits= (1-hit_prob)**(down)* hit_prob**(up)* fact(self.swings)/fa/np.flip(fa)
        
        if re_roll:
            hits= re_roll(hit_prob, self.swings+1, hits)
        elif re_roll_1s:
            hits= re_roll_1s(hit_prob, 1/(self.to_hit-1), self.swings+1, hits)
                
        
        if re_roll_1s:
            crit_fail=1/(selto_hit-1)
            # non_cirt=1-crit_fail
            hits2=np.zeros( self.swings+1)
            for i in range(self.swings+1):
                fails=self.swings-i
                print("fails",fails, hits[i])
                up= np.linspace(0.0,fails,fails+1, endpoint=True)
                fa=fact_array(fails)
                
                
                
                ones= (1-crit_fail)**(np.flip(up))* crit_fail**(up)* fact(fails)/fa/np.flip(fa) * hits[i]
                for j in range(fails+1):
                    up= np.linspace(0.0,j,j+1, endpoint=True)
                    fa=fact_array(j)
                    # print(j, up, ones[j])
                    # print(ones[j] *  (1-hit_prob)**(np.flip(up))* hit_prob**(up)* fact(j)/fa/np.flip(fa))
                    hits2[i:j+i+1] = hits2[i:j+i+1]  +  ones[j] *  (1-hit_prob)**(np.flip(up))* hit_prob**(up)* fact(j)/fa/np.flip(fa)
            # print("rr1",hits2)
            hits=hits2
 


        if any( [self.sustained_hit[0], self.lethal_hit]):        
            crit_prob= (7-crit)/(7-self.to_hit)
            crits= np.zeros((self.swings+1,self.swings+1))
            for hit in range(self.swings+1):
                up= np.linspace(0.0,hit,hit+1, endpoint=True)
                fa=fact_array(hit)
                
                crits[hit, :hit+1] =    (1-crit_prob)**(np.flip(up))* crit_prob**(up)* fact(hit)/fa/np.flip(fa) * hits[hit]
            # print("crits",crits, np.sum(crits))
            
            
            if self.sustained_hit[0] and self.lethal_hit:
                extra=self.sustained_hit[1]
                crits2= np.zeros(( (self.swings*(extra+1))+1, self.swings+1))
                for i in range(self.swings+1):
                    for j in range(self.swings+1):
                        crits2[ i+ j*extra,  j ] =  crits[i,j]
                # print(crits)
                # print()
                # print("crits"crits2)
                return hits, crits2
            elif self.sustained_hit[0]:
                extra=self.sustained_hit[1]
                # if self.lethal_hit:
                        # extra-=1
                hits=np.zeros( (self.swings*(extra+1))+1)

                for i in range(self.swings+1):
                    for j in range(self.swings+1):
                        hits[ i+ j*extra ] = hits[ i+ j*extra ]+ crits[i,j]
                # print("sus",hits, np.sum(hits))
       
                
            elif self.lethal_hit:
                # if not self.sustained_hit[0]:
                    # for i in range(self.swings+1):
                        # hits[i]=0
                        # for j in range(self.swings+1):
                            # if i+j < self.swings+1:
                                # hits[i]+= crits[i+j, j]
                
                # crits=np.sum(crits, axis=0)
                # # print("lethal hits",hits, np.sum(hits))
                # # print("letal crits",crits, np.sum(crits))

                # assert np.sum(hits) ==1.0
                # assert np.sum(crits)==1.0
                # print("hits",hits, np.sum(hits))
                return hits, crits
                
        # print("hits",hits, np.sum(hits))
        assert np.sum(hits)==1.0
        return hits ,None
    
    def get_wounds(self, hit_array,crits, toughness, re_roll=False, re_roll_1s=False):
        if self.twin_linked:
            re_roll=True
        
        # print(hit_array)
        
        if self.strength >= toughness*2:
            wound_prob=5.0/6.0
        elif self.strength > toughness:
            wound_prob=4.0/6.0
        elif self.strength == toughness:
            wound_prob=3.0/6.0
        elif self.strength <= toughness *0.5:
            wound_prob=1.0/6.0
        elif self.strength < toughness:
            wound_prob=2.0/6.0
        
        
        
        if self. lethal_hit:
            # print(hit_array)
            print("crit",crits)
            wounds=np.zeros((crits.shape[1],crits.shape[0],crits.shape[0])) #dice to roll, sucesses, auto wounds
            
            for rolls in range(crits.shape[0]):            
              for auto_wound in range( min(rolls+1, crits.shape[1])):            
                # up= np.tile(np.linspace(0.0,rolls,rolls+1, endpoint=True),   (hit_array.shape[0],1 ) ) 
                 
                up= np.linspace(0.0,rolls-auto_wound,rolls+1-auto_wound, endpoint=True)
                down=np.flip(up)   
                fa=fact_array(rolls-auto_wound)
                # print((crits[rolls,auto_wound]* (1-wound_prob)**(down)).shape)
                # print( (wound_prob**(up)).shape )
                # print( (fact(rolls-auto_wound)/fa/np.flip(fa)).shape)
                # print(wounds[auto_wound, :rolls+1,rolls].shape)
                
                wounds[auto_wound, :rolls+1-auto_wound, rolls-auto_wound]=  crits[rolls,auto_wound]* (1-wound_prob)**(down)* wound_prob**(up)* fact(rolls-auto_wound)/fa/np.flip(fa)
                print(rolls, auto_wound, wounds[auto_wound, :rolls+1-auto_wound,rolls-auto_wound])
                # print(rolls,"wounds", wounds)
            if self.devastating_wound:
                asdf
            else:
                # print("wounds")
                print(wounds)
                
                wounds_temp = wounds[0 ]
                for auto_wound in range(1,hit_array.shape[0]):
                    # print("-")
                    # print(wounds[auto_wound,:-auto_wound, auto_wound: ])
                    wounds_temp[ auto_wound: ] = wounds_temp[ auto_wound:]+ wounds[auto_wound, :-auto_wound ]
                wounds= wounds_temp
                
                print("wounds",wounds)
                wounds = np.sum(wounds, axis=1)
                print("wounds compressed", wounds)
                assert np.sum(wounds)==1.0
                return wounds
        else:
            wounds=np.zeros((hit_array.shape[0],hit_array.shape[0])) #dice to roll, successes

            for rolls in range(hit_array.shape[0]):            
                up= np.linspace(0.0,rolls,rolls+1, endpoint=True)
                down=np.flip(up)   
                fa=fact_array(rolls)
                # print(up, (1-wound_prob)**(down)* wound_prob**(up)* fact(rolls)/fa/np.flip(fa))
                wounds[:rolls+1,rolls]=  hit_array[rolls]* (1-wound_prob)**(down)* wound_prob**(up)* fact(rolls)/fa/np.flip(fa)
                # print(rolls,"wounds", wounds)
        

            if self.devastating_wound:
                asdf
            else:         
                print("wounds",wounds)
                wounds = np.sum(wounds, axis=1)
                print("wounds compressed", wounds)
                assert np.sum(wounds)==1.0
                return wounds
        
        
def load_weapons(file):
    csv_lines = csv.load(file)
    weapons=[]
    for line in csv_lines:
        if len(line) !=6:
            print("!! bad weapon csv line", line)
            assert False
        weapons.append( Weapon( line))