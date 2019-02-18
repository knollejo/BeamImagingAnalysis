"""Provides classes for job submission on different batch systems.

JobSubmitter: Abstract class for job submission.
QSubmitter: Submit jobs on DESY-NAF.
BSubmitter: Submit jobs on CERN-LXBATCH.
"""

from datetime import datetime
from os import getcwd, mkdir
from os.path import exists
from subprocess import call
from uuid import uuid4

if not exists('logs'):
    mkdir('logs')
if not exists('tmp'):
    mkdir('tmp')

class JobSubmitter:
    """Abstract base class for job submission.

    __init__: Create and submit a job.
    cwd: Return current working directory.
    now: Return current time stamp.
    """
    def __init__(
        self, job, args=None, names=None, rt=None, vmem=None, ma=None, mo=False,
        test=False
    ):
        # Submit command
        command = [self.sub()]
        # Log file
        if names is not None:
            names2 = names + [self.now()]
        else:
            names2 = [self.now()]
        output = '{0}/logs/log_{1}.txt'.format(self.cwd(), '_'.join(names2))
        command.append(self.output(output))
        # Mail information
        if ma is not None:
            command.append(self.mail(ma, mo))
        # Run time
        if rt is not None:
            command.append(self.time(rt))
        # CPU memory
        if vmem is not None:
            command.append(self.vmem(vmem))
        # Job name
        if names is not None:
            command.append(self.name('.'.join(names)))
        # Job and arguments
        myjob = [job, self.cwd()]
        if args is not None:
            myjob = myjob + args
        command.append(self.job(myjob))
        if test:
            print ' '.join(command)
        else:
            call(' '.join(command), shell=True)

    @staticmethod
    def cwd():
        return getcwd()

    @staticmethod
    def now():
        return datetime.now().strftime('%y%m%d_%H%M%S')

    def sub(self):
        msg = 'JobSubmitter: Called sub() of abstract class!'
        raise NotImplementedError(msg)

    def output(self, output):
        msg = 'JobSubmitter: Called output() of abstract class!'
        raise NotImplementedError(msg)

    def mail(self, address, option):
        msg = 'JobSubmitter: Called mail() of abstract class!'
        raise NotImplementedError(msg)

    def time(self, hours):
        msg = 'JobSubmitter: Called time() of abstract class!'
        raise NotImplementedError(msg)

    def name(self, name):
        msg = 'JobSubmitter: Called name() of abstract class!'
        raise NotImplementedError(msg)

    def job(self, job):
        msg = 'JobSubmitter: Called job() of abstract class!'
        raise NotImplementedError(msg)

    def vmem(self, mem):
        msg = 'JobSubmitter: Called vmem() of abstract class!'
        raise NotImplementedError(msg)


class QSubmitter(JobSubmitter):
    """Class for job submission on DESY-NAF."""

    def sub(self):
        return 'condor_qsub'

    def output(self, output):
        return '-j y -o {0}'.format(output)

    def mail(self, address, option):
        option = {True: 'eas', False: 'as'}[option]
        return '-m {0} -M {1}'.format(option, address)

    def time(self, hours):
        return '-l h_rt="{0}:00:00"'.format(hours)

    def name(self, name):
        return '-N {0}'.format(name)

    def job(self, job):
        return '"{0}"'.format(' '.join(job))

    def vmem(self, mem):
        return '-l h_vmem="{0}"'.format(mem)


class BSubmitter(JobSubmitter):
    """Class for job submission on CERN-LXBATCH."""

    def sub(self):
        return 'bsub'

    def output(self, output):
        return '-o {0}'.format(output)

    def mail(self, address, option):
        mail = '-u {0}'.format(address)
        if option:
            mail = '{0} -N'.format(mail)
        return mail

    def time(self, hours):
        if hours <= 1:
            queue = '1nh'
        elif hours <= 8:
            queue = '8nh'
        elif hours <= 24:
            queue = '1nd'
        elif hours <= 48:
            queue = '2nd'
        elif hours <= 168:
            queue = '1nw'
        else:
            queue = '2nw'
        return '-q {0}'.format(queue)

    def name(self, name):
        return '-J {0}'.format(name)

    def job(self, job):
        jobfile = job[0]
        jobargs = job[1:]
        with open(jobfile) as f:
            jobcode = f.read()
        for i in range(len(jobargs)):
            jobcode = jobcode.replace('${0}'.format(i+1), jobargs[i])
        newname = 'tmp/{0}_{1}.sh' \
                  .format(jobfile.replace('.', '_').replace('/', '_'), uuid4())
        newline = '\nrm {0}/{1}'.format(self.cwd(), newname)
        jobcode = jobcode + newline
        with open(newname, 'w') as f:
            f.write(jobcode)
        return '< {0}'.format(newname)
