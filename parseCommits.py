from datetime import datetime

def parseCommits(text):
    list_of_commits = []

    if text.count('\n') > 0:
        lines = text.split('\n')
        for item in lines:
            commit = {
                'hesh': '',
                'pointers': '',
                'message': '',
                'date': ''
            }
            hesh = item[0 : item.index('-') - 1]
            commit['hesh'] = hesh

            item = item[item.index('-') + 2 : len(item)]

            if item[0] == '(':
                pointer = item[0 : item.index(')') + 1]
                item = item[item.index(')') + 2 : len(item)]
            else:
                pointer = ''
            commit['pointers'] = pointer

            message = item[0 : item.index('(') - 1]
            commit['message'] = message

            time_text = item[item.index('(') + 1 : len(item) - 1]
            time = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")
            commit['date'] = time

            list_of_commits.append(commit)
    else:
        commit = {
            'hesh': '',
            'pointers': '',
            'message': '',
            'date': ''
        }
        hesh = text[0 : text.index('-') - 1]
        commit['hesh'] = hesh

        text = text[text.index('-') + 2 : len(text)]

        if text[0] == '(':
            pointer = text[0 : text.index(')') + 1]
            text = text[text.index(')') + 2 : len(text)]
        else:
            pointer = ''
        commit['pointers'] = pointer

        message = text[0 : text.index('(') - 1]
        commit['message'] = message

        time_text = text[text.index('(') + 1 : len(text) - 1]
        time = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")
        commit['date'] = time

        list_of_commits.append(commit)
    
    return list_of_commits

