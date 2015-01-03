def find_sentence(ary, cond):
    for index, item in enumerate(ary):
        if((item[0]-1)<cond[0] and (item[1]+1)>cond[1]):
            return ary[index]
        elif(item[1]<cond[0]):
            pass
        elif((item[0]-1)<cond[0] and item[1]<cond[1]):
            _start = item[0]
            _index = index
            while index < len(ary):
                _index = _index+1
                if((ary[_index][1]+1)>cond[1]):
                    _end = ary[_index][1]
                    return((_start, _end))

def isPossible(errors, err):
    possible = False
    try:
        errors.index(err)
        possible = True
    except:
        possible = False
    return possible


def compose(collection, document, filters = 'all'):
    source_version = get_version(document)
    source_language = get_lang(document)
    document = get_document(collection, document)
    text = document['text']
    sentences = document['sentence_offsets']
    text_errors = {}
    e = {}
    c = {}
    a = {}
    for err in document['entities']:
        e[err[0]] = err
    for attr in document['attributes']:
        a[attr[2]] = [attr]
    for note in document['comments']:
        c[note[0]] = [note]
    errors = {}
    errored_sentences = []
    for key in e.keys():
        try:
            a[key]
            _attr = []
            for attr in a[key]:
                _attr.append(attr)
        except:
            _attr = None
        try:
            c[key]
            _note = []
            for note in c[key]:
                _note.append(note)
        except:
            _note = None
        try:
            errors[key]
            if(_attr != None):
                for attr in _attr:
                    errors[key][1].append(attr)
            if(_note != None):
                for note in _note:
                    errors[key][2].append(note)
        except:
            errors[key] = (e[key],[],[])
            if(_attr != None):
                for attr in _attr:
                    errors[key][1].append(attr)
            if(_note != None):
                for note in _note:
                    errors[key][2].append(note)
    _errors = errors
    _tags = {}
    for err in errors.keys():
        _error = errors[err]
        _type = _error[0][1]
        _textual_error = text[_error[0][2][0][0]:_error[0][2][0][1]]
        if(filters == 'all' or isPossible(filters.split('::'), _type)):
            try:
                text_errors[_type.lower()].append(_textual_error)
            except:
                text_errors[_type.lower()] = []
                text_errors[_type.lower()].append(_textual_error)
            _tag = u'<error type="{0}"'.format(_type)
            _revert_offset = len(_tag)
            if _error[1]:
                for e in _error[1]:
                    _tag += u' {0}="{1}" '.format(e[1], e[3])
            _tag += u'><incorrect>{0}</incorrect>'.format(_textual_error)
            if _error[2]:
                for e in _error[2]:
                    _tag += u'<note>{0}</note>'.format(e[2])
            _tag += u'</error>'
            _tags[err] = [_tag, find_sentence(sentences, (_error[0][2][0][0], _error[0][2][0][1])), (_error[0][2][0][0], _error[0][2][0][1])]

    indexes = {}
    for err in errors.keys():
      _error = errors[err]  
      indexes[_error[0][0]] = _error[0][2][0]
    sorted_errors = sorted(indexes.items(), key=operator.itemgetter(1))
    sorted_errors.reverse()

    _last = 0
    _separated_errors = ''
    for error in sorted_errors:
        try:
            if(error[1][1]<_last[1][1]):
                _start = error[1][0]
                _end = error[1][1]
                _begin = text[:_start]
                _ending = text[_end:]

            else:
                _start = error[1][0]
                _end = error[1][1]+_tags[error[0]][1]
                _begin = text[:_start]
                _ending = text[_end:]

                new_tag = sub(r'(<error.*><incorrect>)(.*)(</incorrect>.*</error>)', r'\1'+text[_start:_end]+r'\3', _tags[error[0]][0])

            _last = error
        except:
            _last = error
    text = ''
    for err in _tags.keys():
        _new_sent = '<sentence>'
        _error = _tags[err]
        _sentence = document['text'][_error[1][0]:_error[1][1]]
        _offset = (_error[2][0]-_error[1][0],len(_sentence)-(_error[1][1]-_error[2][1]))
        _new_sent += _sentence[:_offset[0]]+_error[0]+_sentence[_offset[1]:]
        _new_sent += '</sentence>'
        text += u'\n' 
        text += _new_sent
    return text
