
'''
setup.py for rhaptos2

'''

from distutils.core import setup
import os, glob

def get_version():

    '''return version from fixed always must exist file

       Making very broad assumptions about the 
       existence of files '''
    
    v = open('rhaptos2/repo/version.txt').read().strip()
    return v




def main():

    setup(name='rhaptos2.repo',
          version=get_version(),
          packages=['rhaptos2'
                    ,'rhaptos2.repo'
                    ,'rhaptos2.client'
                    ,'rhaptos2.test'
                   ],
          author='See AUTHORS.txt',
          author_email='info@cnx.org',
          url='www.cnx.org',
          license='LICENSE.txt',
          description='New editor / repo / system for cnx.org -rhaptos2.readthedocs.org',
          long_description='see description',
          install_requires=[
              "fabric >= 1.0.0"
              ,"flask >= 0.8"
              ,"statsd"
              ,"requests"
              ,"nose" 
              ,"pylint"
              ,"Flask-OpenID"
              ,"sqlalchemy"
#             sqlite3 - assume its compiled into distrib
                           ],
          scripts=['scripts/rhaptos2_runrepo.py'],

          package_data={'rhaptos2.repo': ['templates/*.*', 'static/*.*', 'version.txt', 'default.ini'],
                        },

#          #intention here is to get setup to use nose to run setup.py test. 
#          tests_require="nose",
#          test_suite="nose.collector",
          
          )



if __name__ == '__main__':
    main()
