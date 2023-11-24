import os
import subprocess
import signal
import time, sys
from daemon import Daemon
from parseCommits import parseCommits
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

class MyDaemon(Daemon):

    def count_commits(self, list_commits, last_time_local):
        count = 0
        for item in list_commits:
            if item['date'] > last_time_local:
                count += 1
        return count
    
    def get_last_remote_commit(self, list_commits, last_time_local):
        last_remote_commit = list_commits[0]
        last_hesh = last_remote_commit['hesh']
        last_time = last_remote_commit['date']

        if last_time > last_time_local:
            return 'Last commit ' + last_hesh + ' ' + str(last_time) + '\n'
        
        return ''

    def get_info(self):
        changes = ''

        fetch = subprocess.check_output("cd " + self.path + " && git fetch", shell=True)

        log = "cd " + self.path + " && git log --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%ad)%Creset' --abbrev-commit --date=format:'%Y-%m-%d %H:%M:%S'"

        output_local = subprocess.check_output(log, shell=True, text=True)
        
        output_remote = subprocess.check_output(log + " main..origin/main", shell=True, text=True)

        if output_remote != '':
            commits_local = parseCommits(output_local)
            self.last_commit_time = commits_local[0]['date']
            self.last_commit_hesh = commits_local[0]['hesh']

            commits_remote = parseCommits(output_remote)

            last_commit = self.get_last_remote_commit(commits_remote, self.last_commit_time)

            if commits_remote[0]['hesh'] == commits_local[0]['hesh'] and commits_remote[0]['date'] == commits_local[0]['date']:
                return ''

            if last_commit != '': 
                changes += last_commit
            
            count = self.count_commits(commits_remote, self.last_commit_time)

            if count != 0:
                changes += 'Total: ' + str(count) + ' new commits'

        return changes


    def run(self):
        self.changes = ''
        while True:
            changes = self.get_info()

            Notify.init("MyDaemon")
            notification = Notify.Notification.new('New commits', changes)

            if changes != '' and changes != self.changes:
                notification.show()

            time.sleep(1)

            self.changes = changes

    def status(self):
        status_text = ''
        pidfile = self.check_pidfile()
        process = self.check_process()
        if pidfile and process:
            status_text = self.statuses['0']
        elif not pidfile and not process:
            status_text = self.statuses['1']
        elif not pidfile and process:
            status_text = self.statuses['2']
            self.kill_all_daemons()
        else:
            status_text = self.statuses['3']
            self.delpid()
        print(status_text)
        return status_text
            
    def kill_all_daemons(self):
        list_of_daemons = subprocess.check_output('pgrep "^python daemon_example.py start|restart$" -f', shell=True, text=True).split('\n')
        for item in list_of_daemons:
            if len(item) > 0:
                os.kill(int(item), signal.SIGTERM)

    def check_pidfile(self):
        return os.path.isfile(self.pidfile)
    
    def check_process(self):
        process = False
        try:
            process = True if subprocess.check_output('pgrep "^python daemon_example.py start|restart$" -f', shell=True, text=True) != '' else False
        except subprocess.CalledProcessError:
            pass
        return process
    
    def check_updates(self):
        fetch = subprocess.check_output("cd " + self.path + " && git fetch", shell=True, text=True)

        log = "cd " + self.path + " && git log --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%ad)%Creset' --abbrev-commit --date=format:'%Y-%m-%d %H:%M:%S'"

        output_local = subprocess.check_output(log, shell=True, text=True)
        
        output_remote = subprocess.check_output(log + " main..origin/main", shell=True, text=True)

        is_update = 'There is no new commits in remote repository'

        if output_remote != '':
            commits_local = parseCommits(output_local)
            self.last_commit_time = commits_local[0]['date']
            self.last_commit_hesh = commits_local[0]['hesh']

            commits_remote = parseCommits(output_remote)

            if commits_remote[0]['hesh'] == commits_local[0]['hesh'] and commits_remote[0]['date'] == commits_local[0]['date']:
                return ''
            
            is_update = self.find_update(commits_remote)

        print(is_update)

        return is_update

    def find_update(self, list_commits):
        for item in list_commits:
            if item['message'].find('Update') != -1 or item['message'].find('update') != -1:
                return 'There is a new update!'
        return 'There is no updates in remote repository'
        

if __name__ == '__main__':

    argum = sys.argv
    path = os.path.dirname(os.path.abspath(__file__))

    daemon = MyDaemon('/tmp/daemon-example.pid', path)

    if argum[1] == 'start':
        daemon.start()
    elif argum[1] == 'stop':
        daemon.stop()
    elif argum[1] == 'restart':
        daemon.restart()
    elif argum[1] == 'status':
        daemon.status()
    elif argum[1] == 'check_updates':
        daemon.check_updates()
    else:
        print('Incorrect arguments')
        sys.exit(1)



