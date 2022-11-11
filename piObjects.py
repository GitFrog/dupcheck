from datetime import datetime
import re

class firstnameObj:

    #def __init__(self):
    def scrub(self, s):
        if s is None or s == "None":
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s



    def sanitize(self, s):
        # done before cleaning
        # uppercase the whole thing
        # replace curly brackets with whitespace
        # removes all numbers and special characters
        # remove leading/trailing whitespace and collapse multiple whitespaces to a single
        s = s.upper()
        s = str.replace(s, ")", " ")
        s = str.replace(s, "(", " ")
        s = re.sub("[^A-Z\s\-]|^\s+|\s+$|[ ]{2,}", "", s)
        return s

    def clean(self, s):
        # this is an interesting one.
        # the only thing I would want to clean at this stage is to remove obvious words that should
        # not be in this field, and perhaps deal with instances of multiple names in this field.
        # (1) Obvious Words: We could come at this two ways. First would be to create a manual cleanup
        #     to compare with. Or to get a little fancier....we could scan the dirty data for any words that
        #     appear more frequently that the most frequent firstnames
        # (2) I think for now if we have more than one name in this field, we should leave it alone. We
        #     simply don't know which is the real first name

        return s

    def bayes(self):
        t=0
        # MICHAEL is the most frequent last name, coming it at 1 in 100 pop freq
        # interestingly....if you account for the top 20 names, you could use 1 in 300 pop freq for all else?
        # wouldn't even need a database for that...could hardcode those names right here.

class middlenameObj:

    #def __init__(self):
    def scrub(self, s):
        if s is None or s == "None":
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s

    def sanitize(self, s):
        s = s.upper()
        s = str.replace(s, ")", " ")
        s = str.replace(s, "(", " ")
        s = re.sub("[^A-Z\s\-]|^\s+|\s+$|[ ]{2,}", "", s) # removes all numbers and special chars
        return s

    def clean(self, s):
        return s

    def bayes(self):
        t = 0
        # MARIE is the most common middle name at 1 in 44 pop freq
        # note that 41% of individuals do not have a recorded middle nanme.

class lastnameObj:

    #def __init__(self):
    def scrub(self, s):
        if s is None or s == "None":
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s

    def sanitize(self, s):
        s = s.upper()
        return s

    def clean(self, s):
        # lets get rid of any words contained within any kind of bracket
        s = str.replace(s, ")", " ")
        s = str.replace(s, "(", " ")
        s = re.sub("[^A-Z\s\-]|^\s+|\s+$|[ ]{2,}", "", s)  # removes all numbers and special chars EXCEPT hyphens
        return s

class dobObj():

    def __init__(self, dateFormat):
        self.dobformat = dateFormat

    def scrub(self, s):
        if s is None:
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s

    def sanitize(self, s):
        # we'll just ba cautious for now and get rid of just whitespace
        #s = re.sub("[\s]|", "", str(s))
        return s

    def clean(self, s):
        # this is where we need to decide on a universal date format.
        #lets go with dd-mm-yyyy
        try:
            dte = datetime.strptime(s, self.dobformat)
            return dte.strftime("%Y-%m-%d")
        except ValueError as e:
            t = e
            return ""

# WORK ON POSSIBLE GEO-CODING OPTIONS
# -------------------------------------

class cityObj():

    #def __init__(self):
    def scrub(self, s):
        if s is None or s == "None":
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s

    def sanitize(self, s):
        s = s.upper()
        s = re.sub("[^A-Z]", "", s)
        return s

    def clean(self, s):
        return s

class postalcodeObj():

    #def __init__(self):
    def scrub(self, s):
        if s is None or s == "None":
            return ""
        else:
            s = self.sanitize(s)
            s = self.clean(s)
            return s

    def sanitize(self, s):
        s = s.upper()
        s = re.sub("[^A-Z0-9]", "", s)
        return s

    def clean(self, s):
        if re.match("^[A-Z]\d[A-Z]?\d[A-Z]\d",s) != None and len(s) == 6: # checks to make sure postalcode is in valid format
            return s
        else:
            return ""

