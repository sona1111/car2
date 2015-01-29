import urwid
import random

class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, id, description):
        self.id = id
        self.content = 'item %s: %s...' % (str(id), description[:25])
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text('item %s' % str(id)), 'body', 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % description), 'body', 'focus'),
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key
        
class MainLayoutWidget (urwid.WidgetWrap):

    def __init__ (self, id, description):
        self.id = id
        self.content = 'item %s: %s...' % (str(id), description[:25])
        
        
        self.item = [
            urwid.LineBox(urwid.Text('vvvvvvvvvvvvvv')),
            urwid.LineBox(urwid.Text('vvvvvvvvvvvvvv'))
        ]
        
        
        w  = urwid.Columns(self.item)
        self.__super.__init__(w)



    def keypress(self, size, key):
        return key

def main ():

    palette = [
        ('body','dark cyan', '', 'standout'),
        ('focus','dark red', '', 'standout'),
        ('head','light red', 'black'),
        ]

    lorem = [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'Sed sollicitudin, nulla id viverra pulvinar.',
        'Cras a magna sit amet felis fringilla lobortis.',
    ]
    
    def keystroke (input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        #if input is 'enter':
        #    focus = listbox.get_focus()[0].content
        #    view.set_header(urwid.AttrWrap(urwid.Text(
        #        'selected: %s' % str(focus)), 'head'))

    

    header = urwid.AttrMap(urwid.Text('Main Menu'), 'head')

    mainwidget = urwid.LineBox(MainLayoutWidget(1,'t'))
    fill = urwid.Filler(mainwidget, 'middle')    
    view = urwid.Frame(fill, header = header)
    
    loop = urwid.MainLoop(view)
    
    loop.run()

if __name__ == '__main__':
    main()
