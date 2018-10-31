from django.contrib import messages


class MessageMixin(object):
    """
    Make it easy to display notification messages when using Class Based Views.
    """
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)
