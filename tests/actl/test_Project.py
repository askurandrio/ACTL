from actl import Project


def test_Project__toStrUsingProjectF():
	project = Project()
	project.processSource([{'setKey': {'key':'projectF', 'value': '/project.yaml'}}])

	assert str(project) == "Project<projectF='/project.yaml'>"


def test_Project__toStrUsingSource():
	project = Project()
	project.processSource([{'setKey': {'key':'key', 'value': 'value'}}])

	assert str(project) == "Project<source=[{'setKey': {'key': 'key', 'value': 'value'}}]>"
