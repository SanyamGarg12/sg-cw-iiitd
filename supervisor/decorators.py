from django.http import Http404
from CW_Portal import access_cache

def supervisor_logged_in(view):
    def _wrapped_view(request, *args, **kwargs):
        if not all([request.user.is_authenticated(), request.user.email in access_cache.get_TA()]):
            raise Http404()
        request.session['noti_count_proposal']      = access_cache.get_noti_count('proposal')
        request.session['noti_count_submissions']   = access_cache.get_noti_count('submissions')
        request.session['noti_count_NGO']           = access_cache.get_noti_count('NGO')

        return view(request, *args, **kwargs)
    return _wrapped_view