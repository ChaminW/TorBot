from modules.net_utils import get_urls_from_page, get_url_status
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors
from threading import Thread
from queue import Queue


def add_green(link):
    colors = Bcolors()
    return '\t' + colors.OKGREEN + link + colors.ENDC


def add_red(link):
    colors = Bcolors()
    return '\t' + colors.On_Red + link + colors.ENDC


def get_links(soup, ext=False, live=False):
    """
        Returns list of links listed on the webpage of the soup passed. If live
        is set to true then it will also print the status of each of the links
        and setting ext to an actual extension such as '.com' will allow those
        extensions to be recognized as valid urls and not just '.tor'.
        Args:
            soup (bs4.BeautifulSoup): webpage to be searched for links.

        Returns:
            websites (list(str)): List of websites that were found
    """
    b_colors = Bcolors()
    if isinstance(soup, BeautifulSoup):
        websites = get_urls_from_page(soup, extension=ext)
        # Pretty print output as below
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')

        if live:
            queue_tasks(websites, display_link)
        return websites

    else:
        raise(Exception('Method parameter is not of instance BeautifulSoup'))


def display_link(link):
    resp = get_url_status(link)
    if resp != 0:
        title = BeautifulSoup(resp.text, 'html.parser').title
        coloredlink = add_green(link)
        print_row(coloredlink, title)
    else:
        coloredlink = add_red(link)
        print_row(coloredlink, "Not found")


def execute_tasks(q, task_func, tasks_args=tuple()):
    while True:
        task = q.get()
        if tasks_args:
            task_func(task, tasks_args)
        else:
            task_func(task)
        q.task_done()


def queue_tasks(tasks, task_func, tasks_args=tuple()):
    q = Queue(len(tasks)*2)
    for _ in tasks:
        if tasks_args:
            if isinstance(tasks_args, tuple):
                t = Thread(target=execute_tasks, args=(q, task_func, tasks_args))
                t.daemon = True
                t.start()
            else:
                raise(Exception('Function arguments must be passed in the form of a tuple.'))
        else:
            t = Thread(target=execute_tasks, args=(q, task_func))
            t.daemon = True
            t.start()

    for task in tasks:
        q.put(task)
    q.join()


def print_row(url, description):
    print("%-80s %-30s" % (url, description))
