import collections


class ChoicesDict(object):

    '''The choices dict is an object that stores a sorted representation of
    the values by key and database value'''

    def __init__(self):
        self._by_value = collections.OrderedDict()
        self._by_key = collections.OrderedDict()

        # Reset the choice creation counter since this will only be accessed
        # after processing the choices
        Choice.order = 0

    def __getitem__(self, key):
        if key in self._by_value:
            return self._by_value[key]
        elif key in self._by_key:
            return self._by_key[key]
        else:
            raise KeyError('Key %r does not exist' % key)

    def __setitem__(self, key, value):
        self._by_key[key] = value
        self._by_value[value.value] = value

    def __iter__(self):
        for k, v in self._by_value.iteritems():
            yield k, v

    def items(self):
        return list(self)

    def __repr__(self):
        return repr(self._by_key)

    def __str__(self):
        return str(self._by_key)


class Choice(object):

    '''The choice object has an optional label and value. If the value is not
    given an autoincrementing id (starting from 1) will be used'''
    order = 0

    def __init__(self, value=None, label=None):
        Choice.order += 1
        self.value = value
        self.label = label
        self.order = Choice.order

    def __repr__(self):
        return (u'<%s[%d]:%s>' % (
            self.__class__.__name__,
            self.order,
            self.label,
        )).encode('utf-8', 'replace')

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')

    def __unicode__(self):
        value = self.value
        if isinstance(value, str):
            return unicode(value, 'utf-8', 'replace')
        else:
            return unicode(value)


class ChoicesMeta(type):

    '''The choices metaclass is where all the magic happens, this
    automatically creates a ChoicesDict to get a sorted list of keys and
    values'''

    def __new__(cls, name, bases, attrs):
        choices = list()
        has_values = False
        for key, value in attrs.iteritems():
            if isinstance(value, Choice):
                if value.value:
                    has_values = True

                if not value.label:
                    value.label = key

                choices.append((key, value))

        attrs['choices'] = ChoicesDict()
        i = 0
        for key, value in sorted(choices, key=lambda c: c[1].order):
            if has_values:
                assert value.value, ('Cannot mix choices with and without '
                                     'values')
            else:
                value.value = i
                i += 1

            attrs[key] = value.value
            attrs['choices'][key] = value

        return super(ChoicesMeta, cls).__new__(cls, name, bases, attrs)


class Choices(object):

    '''The choices class is what you should inherit in your Django models'''
    __metaclass__ = ChoicesMeta