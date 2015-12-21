
dict_file_name = 'c10.bin'

gid_dict = {}
ggid_dict = {}
mgid_dict = {}


        
def load(fname = None):
    global dict_file_name
    if fname:
        dict_file_name = fname

    def add(dic, key, addkey, *arg):
        # make set
        try:
            s = dic[key]
        except KeyError:
            s = set()
            if addkey:
                s.add(key)
            dic.update({ key:s })

        # update
        s.update(set(arg))
        
            

    # read file
    if dict_file_name.endswith('.txt'):
        f = open(dict_file_name, 'r')
        line = f.readline()
        while line:
            # read line
            tk = line.split()
            
            # gid
            gid = int(tk[0])

            if gid % 2:
                ggid = int(tk[1])
                arc = float(tk[3])
                entry = (ggid, arc)
                if gid_dict.has_key(gid + 1):
                    entry = gid_dict[gid + 1] + entry
                    gid_dict[gid + 1] = entry
                    add(mgid_dict, entry[0], True, gid, entry[3])
                else:
                    gid_dict.update({ gid:entry })
                    
                # add to granule dict
                add(ggid_dict, ggid, False, gid)
            else:
                entry = (int(tk[1]), int(tk[2]), float(tk[3]))
                try:
                    entry_odd = gid_dict[gid - 1]
                    entry += entry_odd
                    del gid_dict[gid - 1]
                    # mgid dict add
                    add(mgid_dict, entry[0], True, gid, entry_odd[0])
                except KeyError:
                    pass
                gid_dict.update({ gid:entry })
                
            line = f.readline()
        f.close()
    else:
        from struct import unpack
        f = open(dict_file_name, 'rb')
        rec = f.read(22)
        while rec:
            # read one record
            mg_gid, mgid, isec, xm, ggid, xg = unpack('>LLHfLf', rec)
            gid_dict.update({ mg_gid:(mgid, isec, xm, ggid, xg) })
            add(ggid_dict, ggid, False, mg_gid - 1)
            add(mgid_dict, mgid, True, mg_gid, ggid)
            rec = f.read(22)
        f.close()


       
def query(gid, verbrec=False):
    from params import Nmitral as nmitral, gid_granule_begin
    from granules import Ngranule
    
    if gid < nmitral:
        descr = 'Mitral soma %d' % gid
        isec = -1
        x = 0.
    elif gid >= gid_granule_begin and gid < (gid_granule_begin + Ngranule):
        descr = 'Granule soma %d' % gid
        isec = 0
        x = 0.
    elif gid % 2:
        info = gid_dict[gid + 1]
        descr = 'Granule %d(%.3g)-%d' % ((info[2], info[4], gid))
        gid = info[3]
        isec = 0
        x = info[4]
    else:
        info = gid_dict[gid]
        descr = 'Mitral %d[%d](%.3g)-%d' % (info[:3] + (gid, ))
        gid, isec, x = info[:3]

        
    if verbrec:
        print descr
        print '\n if you want use on vrecord write this params'
        print '\t (' + str(gid) + ', ' + str(isec) + ', ' + str(x) + ')'
        
    return gid, isec, x, descr
