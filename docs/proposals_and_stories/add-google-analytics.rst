

Add Google Analytics support
============================

The author(s) of modules and collections should be able to add their own
tracking codes to a module or collection or both, and we should offer a facility to do this.

:storyref: https://trello.com/card/repo-add-api-support-for-new-metadata-fields-4-pts/5181197901c3b1290b001951/86

Spec
----



We shall provide a single text field in both modules and collections named 
``gac`` and this will allow arbitrary tracking code to be installed.

The backend repo only needs to support accepting a new field from the json doc
and handling it correctly.  The ATC client will need to do more, see story https://trello.com/card/atc-add-missing-ui-fields-for-metadata-6-pts/5181197901c3b1290b001951/85


Security issue: It may be better to implement this as a google-only field,
and capture only a string corresponding to the google tracking code (ie AM-1234ABB) and we fill in the script boiler plate around it.  This will prevent arbitrary script being written into the modules.  An skype discussion indicated we would sanitise all HTML inputs during the publication process.


Tests
-----

* Can we inject a arbitrary string?
* Can we see same string returned with no HTML mangling?
