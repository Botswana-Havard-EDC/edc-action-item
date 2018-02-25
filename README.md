# edc-action-items

[![Build Status](https://travis-ci.org/botswana-harvard/edc-action-item.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-action-item) [![Coverage Status](https://coveralls.io/repos/github/botswana-harvard/edc-action-item/badge.svg?branch=develop)](https://coveralls.io/github/botswana-harvard/edc-action-item?branch=develop)

Add subject related action items to the Edc.

### Overview

Action items are reminders to submit a form.

Action items can be configured to drive data collection
* for forms that do not fit well in a visit schedule; 
* for forms that are required based on some clinical event. 

Action items have are tracked. Each is allocated a unique `action_identifier` and maintain status (New, Open, Closed).

Actions can be chained. One action can create another `next` action.

### Adverse Events, Death, OffSchedule are all good candidates.

Adverse Event reports are required based on some clinical event. Since the event must be reported, leaving the decision to report the user is not sufficient. An action item can be opened based on the clinical event and the status of the action item tracked administratively. The action item is associtaed with the AE report. Once the report is submitted, the action item closes. If additional data is required after an initial AE report is submitted, a follow-up action can automatically be opened.

See module `ambition-ae.action_items` for examples. 

### Defining an action items

In the root of your App, define an `action_item` module. The edc-action-item site controller will autodiscover this module and register the action item classes.

To register action item classes:
    
    site_action_items.register(AeInitialAction)


### A simple action item

In it define actions using the `Action` class.

    from edc_action_item import Action, site_action_items
    from ambition_ae.action_items import AeFollowupAction, AeTmgAction

    class AeInitialAction(Action):
    
        name = AE_INITIAL_ACTION
        display_name = 'Submit AE Initial Report'
        model = 'ambition_ae.aeinitial'
        show_on_dashboard = True
        instructions = 'Complete the initial report and forward to the TMG'
        priority = HIGH_PRIORITY

The action item is associated with its model

    from edc_action_item.model_mixins import ActionItemModelMixin
    from edc_identifier.managers import TrackingIdentifierManager
    from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
    from edc_identifier.model_mixins import TrackingIdentifierModelMixin
    
    class AeInitial(ActionItemModelMixin, NonUniqueSubjectIdentifierFieldMixin,
                    TrackingIdentifierModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AE'

    action_cls = AeInitialAction
    
    ... # field classes
    
    objects = TrackingIdentifierManager()
    
Somewhere in your code, instantiate the action item

    AeInitialAction(subject_identifier='12345')
    
This creates an `ActionItem` model instance for this subject with a `status` of `New` (if it does not exist).

Now create the associated model instance

    AeInitial.objects.create(subject_identifier='12345', ...)
    
The `ActionItem` model instance now has a status of `Closed`.


### Singleton action items

To ensure an action item does not create more than one instance per subject, use the `singleton` attribute.

    class EnrollToSubstudyAction(Action):
        name = 'My Action'
        display_name = 'Enroll to sub-study'
        model = 'myapp.enroll'
        show_link_to_changelist = True
        admin_site_name = 'myapp_admin'
        priority = HIGH_PRIORITY
        create_by_user = False
        singleton=True

### Action items that create a `next` action item

For an action item to open another action item(s) once closed, set `next_actions`.

    class AeInitialAction(Action):
    
        name = AE_INITIAL_ACTION
        display_name = 'Submit AE Initial Report'
        model = 'ambition_ae.aeinitial'
        show_on_dashboard = True
        instructions = 'Complete the initial report and forward to the TMG'
        priority = HIGH_PRIORITY
        next_actions = [AeFollowupAction]

If the criteria for the next action is based on some other information declare `get_next_actions` on the action item and return the list of action items needed.

    class AeInitialAction(Action):

    ...
    
    def get_next_actions(self):
        next_actions = []
        try:
            self.reference_model_cls().objects.get(
                ae_initial=self.model_obj.ae_initial)
        except MultipleObjectsReturned:
            pass
        else:
            if (self.model_obj.ae_initial.ae_classification
                    != self.model_obj.ae_classification):
                next_actions = [self]
        return next_actions
 