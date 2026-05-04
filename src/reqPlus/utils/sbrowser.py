

import browserforge.headers

def gibe_random_ua(*args,**kw):
    _headers = browserforge.headers.HeaderGenerator()
    headers = _headers.generate()
    return browserforge.headers.generator.get_user_agent(headers)
