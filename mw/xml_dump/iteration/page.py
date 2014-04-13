from ...types import serializable
from ...util import none_or

from .revision import Revision

class Page(serializable.Type):
	"""
	Page meta data and a :class:`mw.xml_dump.Revision` iterator.  Instances of 
	this class can be called as iterators directly.  E.g.::
	
		page = mw.xml_dump.Page( ... )
		
		for revisions in page:
			# Do things with revision and/or page
		
	"""
	__slots__ = (
		'id',
		'title',
		'namespace',
		'redirect',
		'restrictions',
		'revisions'
	)
	
	def __init__(self, id, title, namespace, redirect, restrictions, revisions):
		self.id = none_or(id, int)
		"""
		Page ID : int
		"""
		
		self.title = none_or(title, str)
		"""
		Page title (namespace excluded) : str
		"""
		
		self.namespace = none_or(namespace, int)
		"""
		Namespace ID : int
		"""
		
		self.redirect = none_or(redirect, str)
		"""
		Page is currently redirect? : bool
		"""
		
		self.restrictions = none_or(restrictions, str)
		"""
		TODO: ??? : str
		"""
		
		# Should be a lazy generator
		self.__revisions = revisions
		
	
	def __iter__(self):
		return self.__revisions
		
	def __next__(self):
		return next(self.__revisions)
	
	@classmethod
	def load_revisions(cls, first_revision, element):
		yield Revision.from_element(first_revision)
		
		for sub_element in element:
			tag = sub_element.tag
			
			if tag == "revision":
				yield Revision.from_element(sub_element)
			else:
				raise MalformedXML("Expected to see 'revision'.  " + \
					               "Instead saw '{0}'".format(tag))
			
	
	@classmethod
	def from_element(cls, element):
		title        = None
		namespace    = None
		id           = None
		redirect     = None
		restrictions = None
		
		first_revision = None
		
		# Consume each of the elements until we see <id> which should come last.
		for sub_element in element:
			tag = sub_element.tag
			if tag == "title":
				title = sub_element.text
			elif tag == "ns":
				namespace = sub_element.text
			elif tag == "id":
				id    = int(sub_element.text)
			elif tag == "redirect":
				redirect = sub_element.attr("title", None)
			elif tag == "restrictions":
				restrictions = sub_element.text
			elif tag == "revision":
				first_revision = sub_element
				break
				# Assuming that the first revision seen marks the end of page 
				# metadata.  I'm not too keen on this assumption, so I'm leaving
				# this long comment to warn whoever ends up maintaining this. 
			else:
				raise MalformedXML("Unexpected tag found when processing " + \
					               "a <page>: '{0}'".format(tag))
		
		# Assuming that I got here by seeing a <revision> tag.  See verbose
		# comment above. 
		revisions = cls.load_revisions(first_revision, element)
		
		
		return cls(id, title, namespace, redirect, restrictions, revisions)


