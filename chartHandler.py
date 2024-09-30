# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 16:02:22 2024

@author: seer2
"""
import numpy as np
import re
import json
class chartDecomposer():
    def __init__(self): #list where each element stands for a line
        #定数
        self.rating_num = 0
        #V slide reference matrix
        self.begin_to_mid = np.array([[0,0,1,0,0,0,1,0],
                                      [0,0,0,1,0,0,0,1],
                                      [1,0,0,0,1,0,0,0],
                                      [0,1,0,0,0,1,0,0],
                                      [0,0,1,0,0,0,1,0],
                                      [0,0,0,1,0,0,0,1],
                                      [1,0,0,0,1,0,0,0],
                                      [0,1,0,0,0,1,0,0]])
        self.mid_to_end = np.array([[0,0,7,9,9,9,3,0],
                                    [0,0,0,8,9,9,9,4],
                                    [5,0,0,0,1,9,9,9],
                                    [9,6,0,0,0,2,9,9],
                                    [9,9,7,0,0,0,3,9],
                                    [9,9,9,8,0,0,0,4],
                                    [5,9,9,9,1,0,0,0],
                                    [0,6,9,9,9,2,0,0]])
        
        #Tap recorder
        self.tap = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.xtap = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        
        #Hold recorder
        self.hold = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.xhold = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}

        #Touch (hold) recorder
        self.A = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.B = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.C = {1:[],2:[]}
        self.Ch = []
        self.D = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.E = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.touch = {'A':self.A, 'B':self.B, 'C':self.C, 'D':self.D, 'E':self.E} 
        
        #Slide recorder
        self.slide = {}
        self.bslide = {}
        for begin in range(1,9):
            self.slide[begin] = {}
            self.bslide[begin] = {}
            #添加星星形状层级            
            for shape in ['-', '^', '<', '>', 'v', 'p', 'q', 's', 'z', 'w', 'pp', 'qq']:
                self.slide[begin][shape] = {}
                self.bslide[begin][shape] = {}
                
            for end in range(1,9):
                #直线星星'-'
                if abs(begin-end) != 0 and abs(begin-end) != 1 and abs(begin-end) != 7:
                    self.slide[begin]['-'][end] = []
                    self.bslide[begin]['-'][end] = []
                
                #Short arc '^'、V型星星'v'
                if begin != end and abs(begin-end) != 4:
                    self.slide[begin]['^'][end] = []
                    self.slide[begin]['v'][end] = []
                    self.bslide[begin]['^'][end] = []
                    self.bslide[begin]['v'][end] = []

                #逆时针'<'，顺时针'>'，‘p’型，‘q’型，‘pp’型，‘qq’型
                for shape in ['<','>','p','q','pp','qq']:
                    self.slide[begin][shape][end] = []
                    self.bslide[begin][shape][end] = []

                #闪电星星's','z',wifi星星'w'
                for shape in ['s','z','w']:
                    if abs(begin-end) == 4:
                        self.slide[begin][shape][end] = []
                        self.bslide[begin][shape][end] = []

            #大V星星'V'
            self.slide[begin]['V'] = {}
            self.bslide[begin]['V'] = {}
            for mid in range(1,9):
                if self.begin_to_mid[begin-1][mid-1] == 1:
                    self.slide[begin]['V'][mid] = {}
                    self.bslide[begin]['V'][mid] = {}
                    for end in range(1,9):
                         if self.mid_to_end[mid-1][end-1] == 9 or self.mid_to_end[mid-1][end-1] == begin:
                             self.slide[begin]['V'][mid][end] = []
                             self.bslide[begin]['V'][mid][end] = []
        #Break tap recorder
        self.btap = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.bxtap = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}

        #Break hold recorder
        self.bhold = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        self.bxhold = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}

    def remove_consecutive_duplicates(self, input_list):
        if not input_list:
            return []

        result = [input_list[0]]  # Initialize with the first element
        for i in range(1, len(input_list)):
            if input_list[i] != input_list[i - 1]:  # Compare with the previous element
                result.append(input_list[i])

        return result

    def remove_repeated_slide(self):
        for begin in self.slide.keys():
                for shape in self.slide[begin].keys():
                    if shape != 'V':
                        for end in self.slide[begin][shape].keys():
                            self.slide[begin][shape][end] = self.remove_consecutive_duplicates(self.slide[begin][shape][end])
                            self.bslide[begin][shape][end] = self.remove_consecutive_duplicates(self.bslide[begin][shape][end])
                    else:
                        for mid in self.slide[begin][shape].keys():
                            for end in self.slide[begin][shape][mid].keys():
                                self.slide[begin][shape][mid][end] = self.remove_consecutive_duplicates(self.slide[begin][shape][mid][end])
                                self.bslide[begin][shape][mid][end] = self.remove_consecutive_duplicates(self.bslide[begin][shape][mid][end])
    
    def output_data(self):
        self.remove_repeated_slide()
        note = {'tap' : self.tap,
                  'btap' : self.btap,
                  'xtap' : self.xtap,
                  'bxtap' :self.bxtap,
                  'hold' : self.hold,
                  'bhold' : self.bhold,
                  'xhold' : self.xhold,
                  'bxhold' :self.bxhold,
                  'touch' : self.touch,
                  'slide' : self.slide,
                  'bslide' : self.bslide}
        return {'rating_num' : self.rating_num, 'note' : note}
        
    def fetch_slice_in_string(self, text, start_index, target):
        if start_index == len(text)-1:
            return [text[start_index], start_index]
        else:
            if text[start_index] == target:
                return [target, start_index]
            else:
                result = self.fetch_slice_in_string(text, start_index + 1, target)
                return [text[start_index] + result[0], result[1]]

    def take_out_piece_by_index(self, text, start_index, end_index):
        first_half = text[:start_index]
        #print('firsthalf:',first_half)
        #print(text, start_index, end_index)
        if end_index == len(text)-1:
            second_half = ''
        else:
            second_half = text[end_index+1:]
        #print('second_half:',second_half)
        return first_half + second_half

    
    def decompose(self, fullchart): #非纯粹谱面文件，database[n][difficulty][diff]
        cur_time = 0
        self.rating_num = fullchart['rating_num']
        for line in fullchart['chart']:
            #print(line)
            cur_time = self.decompose_line(line, cur_time)

    def decompose_line(self, line, cur_time):
        #print(line)
        element = line
        #elements = line.split(',')
        #if elements[-1] == '':
            #del elements[-1]
        #print(elements)
        #element = elements[0]
        #print(element)
        
        #print(element)
        #Find几分音
        assert element.find('{') != -1, '几分音信息缺失'
        [beat_frac_text, end_index] = self.fetch_slice_in_string(element, element.find('{'), '}')
        beat_frac = int(beat_frac_text.strip('{').strip('}'))
        #print(beat_frac)
        element = self.take_out_piece_by_index(element, element.find('{'), end_index)
        #print(element)
        #elements[0] = element.strip(',')
        elements = element.split(',')
        del elements[-1]
        #print(elements)
        cur_bpm = 0
        for element in elements:
            #print(element)
            cur_time = self.decompose_same_time_element(element, beat_frac, cur_time, cur_bpm)
        return cur_time

    
    def decompose_same_time_element(self, element, beat_frac, cur_time, cur_bpm):
        #处理具体note
        notes = element.split('/')
        for note in notes:
            self.analyze_single_element(note, beat_frac, cur_time, cur_bpm)
            cur_time += 1/beat_frac
        return cur_time

    def analyze_single_element(self, note, beat_frac, cur_time, cur_bpm):
        #识别bpm
        if len(note) > 0:
            if note[0] == '(':
                bpm_text = note[1:note.find(')')]
                note = note[note.find(')')+1:]
                cur_bpm = float(bpm_text)
                self.push_element(('bpm', cur_bpm), 'all')
        
        #识别tap
        if len(note) == 1 and note[0].isnumeric():
            self.tap[int(note[0])].append((cur_time, None))
            return cur_bpm

        #识别ex tap
        if len(note) == 2:
            if note[0].isnumeric() and note[1] == 'x':
                self.tap[int(note[0])].append((cur_time, None))
                self.xtap[int(note[0])].append((cur_time, None))
                return cur_bpm

        #识别break tap
        if len(note) == 2: 
            if note[0].isnumeric() and note[1] == 'b':
                self.tap[int(note[0])].append((cur_time, None))
                self.btap[int(note[0])].append((cur_time, None))
                return cur_bpm

        #识别break ex tap
        if len(note) == 3:
            if note[0].isnumeric() and note[1] == 'b' and note[2] == 'x':
                self.tap[int(note[0])].append((cur_time, None))
                self.xtap[int(note[0])].append((cur_time, None))
                self.btap[int(note[0])].append((cur_time, None))
                self.bxtap[int(note[0])].append((cur_time, None))
                return cur_bpm

        #识别hold
        if len(note) > 3:
            if note[0].isnumeric() and note[1:3] == 'h[':
                beat_frac, num_of_frac = self.get_duration(note[2:])
                self.hold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                return cur_bpm

        #识别ex hold
        if len(note) > 4:
            if note[0].isnumeric() and 'h' in note[1:3] and 'x' in note[1:3] and note[3] == '[':
                beat_frac, num_of_frac = self.get_duration(note[3:])
                self.hold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                self.xhold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                return cur_bpm

        #识别break hold
        if len(note) > 4:
            if note[0].isnumeric() and 'h' in note[1:3] and 'b' in note[1:3] and note[3] == '[':
                beat_frac, num_of_frac = self.get_duration(note[3:])
                self.hold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                self.bhold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                return cur_bpm

        #识别break ex hold
        if len(note) > 5:
            if note[0].isnumeric() and 'h' in note[1:4] and 'b' in note[1:4] and 'x' in note[1:4] and note[4] == '[':
                beat_frac, num_of_frac = self.get_duration(note[4:])
                self.hold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                self.bhold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                self.xhold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                self.bhold[int(note[0])].append((cur_time, num_of_frac / beat_frac))
                return cur_bpm

        #识别touch
        #print(note)
        if len(note) == 2 or len(note) == 3:
            if note[0].isalpha() and note[1].isnumeric():
                self.touch[note[0]][int(note[1])].append((cur_time, None))
                return cur_bpm

        #识别touch hold
        if len(note) >= 3:
            if (note[0:3] == 'Ch[' or note[0:4] == 'C1h[' or note[0:4] == 'C2h['  or note[0:5] == 'C1fh[' 
                or note[0:5] == 'C2fh[' or note[0:5] == 'C1hf[' or note[0:5] == 'C2hf['):
                left_bracket = re.compile(r'\[')
                right_bracket = re.compile(r'\]')
                begin = 0
                end = 0
                for idx in left_bracket.finditer(note):
                    begin = idx.start()
                for idx in right_bracket.finditer(note):
                    end = idx.end()
                beat_frac, num_of_frac = self.get_duration(note[begin:end])
                self.Ch.append((cur_time, num_of_frac / beat_frac))
                return cur_bpm

        #识别slide
        if len(note) >= 5:
            slides = note.split('*')
            head, slide = self.chop_head(slides[0])
            do_register_head = True
            for slide in slides:
                if not slide[0].isnumeric():
                    slide = head + slide
                #print(slide)
                head, slide = self.chop_head(slide)
                self.decompose_slides(head, slide, cur_time, cur_bpm, do_register_head)
                do_register_head = False
                return cur_bpm
                
        return cur_bpm
            #for basic_slide in basic_slide_info_blocks:
                #pass
                
    def chop_head(self, slide):
        flag = True
        cur = 0
        while flag:
            cur += 1
            flag = slide[cur] == 'b' or slide[cur] == 'x'
        return slide[:cur], slide[cur:]

    def decompose_slides(self, head, slide, cur_time, cur_bpm, do_register_head):
        #print(head+slide)
        #print(slide)
        #解读星星语法
        #head, slide = self.chop_head(slide)
        #'-', '^', '<', '>', 'v', 'p', 'q', 's', 'z', 'w', 'pp', 'qq'
        node = re.compile(r'(qq|pp|-|\^|<|>|v|p|q|s|z|w|V)[1-8]([1-8]|)(b|)(\[|)') #shape + position + [
        matches = node.finditer(slide)
        
        node_store = []
        for match in matches:
            target = slide[ match.start() : match.end()]
            if target[-1] == '[':
                target = target[:-1]
            node_store.append(target)
        #print(node_store)
        
        left_bracket = re.compile(r'\[')
        right_bracket = re.compile(r'\]')
        left_store = []
        right_store = []
        interval_store = []
        left_match = left_bracket.finditer(slide)
        right_match = right_bracket.finditer(slide)
        
        for left in left_match:
            left_store.append(left.start())
        for right in right_match:
            right_store.append(right.end())
        for i in range(len(left_store)):
            interval_store.append(slide[ left_store[i] : right_store[i] ])
        #print(interval_store)
        timing = []
        '''
        Waiting time is one beat at 160 BPM, tracing length is three 8th notes at 160 BPM ... 【1-4[160#8:3],】
        Waiting time is one beat at 160 BPM, tracing length is 2 seconds ... 【1-4[160#2],】
        Waiting time is 3 seconds, tracing length is 1.5 seconds ... 【1-4[3##1.5],】
        Waiting time is 3 seconds, tracing length is three 8th notes at current BPM ... 【1-4[3##8:3],】
        Waiting time is 3 seconds, tracing length is three 8th notes at 160 BPM ... 【1-4[3##160#8:3],】
        '''
        for interval in interval_store:
            delay = 0
            if '#' in interval:
                if ':' not in interval: #滑动单位为秒
                    if '##' in interval: #延迟单位为秒
                        [delay, duration] = interval.strip('[').strip(']').split('##')
                        delay = float(delay) / 60 * cur_bpm / 4
                    else: #延迟单位为拍
                        [delay, duration] = interval.strip('[').strip(']').split('#')
                        delay = cur_bpm / float(delay) / 4
                    duration = float(duration) / 60 * cur_bpm / 4
                    timing.append(duration)
                else:
                    if '##' not in interval:
                        [delay, duration] = interval.strip('[').strip(']').split('##')
                        delay = cur_bpm / float(delay) / 4
                        beat_frac, num_of_frac = self.get_duration(duration)
                        timing.append(num_of_frac / beat_frac)
                    else:
                        pattern = re.compile(r'([0-9]|)[0-9]##([0-9]|)([0-9]|)([0-9]|)([0-9]):([0-9]|)([0-9]|)([0-9]|)([0-9])')
                        result = pattern.search(interval)
                        if result:
                            [delay, duration] = result.group().split('##')
                            delay = float(delay) / 60 * cur_bpm / 4
                            duration = '[' + duration + ']'
                            beat_frac, num_of_frac = self.get_duration(duration)
                            timing.append(num_of_frac / beat_frac)
                        else:
                            [delay, second_half] = interval.strip('[').strip(']').split('##')
                            [bpm, duration] = second_half.split('#')
                            delay = float(delay) / 60 * cur_bpm / 4
                            duration = '[' + duration + ']'
                            beat_frac, num_of_frac = self.get_duration(duration)
                            timing.append(num_of_frac / beat_frac*cur_bpm/float(bpm))
            else:
                beat_frac, num_of_frac = self.get_duration(interval)
                timing.append(num_of_frac / beat_frac)
            #timing = [ self.get_duration(interval) for interval in interval_store ]
            if len(timing) == 1:
            #print(node_store)
                duration = timing[0] / len(node_store)
                timing = [duration for i in range(len(node_store))]

            #创造星星object并制造info_block
            this_chained_slide = chainedSlideRegister()
            this_chained_slide.compose_chain(head, node_store, timing)
            info_dicts = this_chained_slide.prepare_info_blocks()

            #添加星星
            temp_time = cur_time
            for i in range(len(info_dicts)):
                #{'begin':self.begin, 'shape':self.shape, 'end':self.end, 'duration':self.duration}
                begin = info_dicts[i]['begin']
                shape = info_dicts[i]['shape']
                mid = info_dicts[i].get('mid',0)
                end = info_dicts[i]['end']
                duration = info_dicts[i]['duration']
                #duration = num_of_frac / beat_frac
                #Grand V
                #print(temp_time+delay)
                if mid != 0:
                    self.slide[begin][shape][mid][end].append((temp_time + delay, duration))
                    
                    if this_chained_slide.is_break():
                        self.bslide[begin][shape][mid][end].append((temp_time + delay, duration))
                #其他星星
                else:
                    self.slide[begin][shape][end].append((temp_time + delay, duration))
                    #print(self.slide[begin][shape][end][-1])
                    #print(self.slide[begin][shape][end][-2])
                    if this_chained_slide.is_break():
                        self.bslide[begin][shape][end].append((temp_time + delay, duration))
                #print(duration)
                #print(temp_time)
                #print('duration='+str(duration))
                temp_time += duration

        #添加星星头tap
        if do_register_head:
            begin = this_chained_slide.head
            self.tap[begin].append((cur_time, None))
            if this_chained_slide.bhead:
                self.btap[begin].append((cur_time, None))
            if this_chained_slide.xhead:
                self.xtap[begin].append((cur_time, None))
            if this_chained_slide.bhead and this_chained_slide.xhead:
                self.bxtap[begin].append((cur_time, None))

    def get_duration(self, text):
        #text: [m:n]
        #print(text)
        beat_frac = text[ 1 : text.find(':') ]
        num_of_frac = text[ text.find(':')+1 : -1]
        beat_frac = int(beat_frac)
        num_of_frac = int(num_of_frac)        
        return beat_frac, num_of_frac
        
    def push_element(self, info_block, note_type):
        #info_block = [cur_time/bpm(str), last_time/bpm]
        if note_type == 'all':
            self.C[1].append(info_block)
            self.C[2].append(info_block)
            self.Ch.append(info_block)
            for key in range(1,9):
                self.tap[key].append(info_block)
                self.xtap[key].append(info_block)
                self.btap[key].append(info_block)
                self.bxtap[key].append(info_block)

                self.hold[key].append(info_block)
                self.xhold[key].append(info_block)
                self.bhold[key].append(info_block)
                self.bxhold[key].append(info_block)

                self.A[key].append(info_block)
                self.B[key].append(info_block)
                self.D[key].append(info_block)
                self.E[key].append(info_block)

            for begin in self.slide.keys():
                for shape in self.slide[begin].keys():
                    if shape != 'V':
                        for end in self.slide[begin][shape].keys():
                            self.slide[begin][shape][end].append(info_block)
                    else:
                        for mid in self.slide[begin][shape].keys():
                            for end in self.slide[begin][shape][mid].keys():
                                self.slide[begin][shape][mid][end].append(info_block)



class basicSlideRegister():
    def __init__(self, shape):
        self.begin = None
        self.shape = shape
        self.end = None
        self.duration = None
        self.delay = 0

    def register(self, begin, end, duration):
        self.begin = int(begin)
        self.end = int(end)
        self.duration = duration

    def prepare_info_block(self):
        return {'begin':self.begin, 'shape':self.shape, 'end':self.end, 'duration':self.duration}



class grandVSlideRegister(basicSlideRegister):
    def __init__(self):
        super().__init__('V')
        self.mid = None

    def register(self, begin, mid, end, duration):
        self.begin = int(begin)
        self.mid = int(mid)
        self.end = int(end)
        self.duration = duration

    def prepare_info_block(self):
        return {'begin':self.begin, 'shape':self.shape, 'mid':self.mid, 'end':self.end, 'duration':self.duration}
    
    
    

class chainedSlideRegister():
    def __init__(self):
        self.chain = []
        self.juezan = False
        self.head = None
        self.bhead = False
        self.xhead = False

    def is_break(self):
        return self.juezan

    def is_break_head(self):
        return self.bhead

    def is_ex_head(self):
        return self.xhead
        
    def compose_chain(self, head, node_store, interval_store):
        #print(head)
        self.head = int(head[0])
        begin = [head[0]]
        shapes = []
        end = []
        shape = re.compile(r'(qq|pp|-|\^|<|>|v|p|q|s|z|w|V)')
        #print(node_store)
        for node in node_store:
            matches = shape.finditer(node)
            for match in matches:
                shapes.append( node[ match.start() : match.end() ] )
                position = node[match.end():]
                #是否为绝赞星星
                if 'b' in position:
                    self.juezan = True
                    position = position[:-1] #=剔除绝赞标识

                begin.append(position)
                end.append(position)
        #print(interval_store)
        del begin[-1]
        #print(begin)
        #print(end)
        for i in range(len(shapes)):
            if shapes[i] != 'V':
                cur_slide = basicSlideRegister(shapes[i])
                cur_slide.register(begin[i][-1], end[i][-1], interval_store[i])
            else:
                cur_slide = grandVSlideRegister()
                cur_slide.register(begin[i][-1], end[i][0], end[i][-1], interval_store[i])
            self.chain.append(cur_slide)

        if 'b' in head:
            self.bhead = True
        if 'x' in head:
            self.xhead = True
        self.head = int(head[0])
            

    def prepare_info_blocks(self):
        return [slide.prepare_info_block() for slide in self.chain]
            
        