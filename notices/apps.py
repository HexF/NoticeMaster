from django.apps import AppConfig


class NoticesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notices'

    school_name = "unknown"

    period_times = dict()
    period_names = dict()

    def ready(self):
        from notices.utils import kamar_api_query
        settings = kamar_api_query("GetSettings")
        d = dict()
        for setting in settings:
            d[setting.tag] = setting.text

        self.school_name = d["SchoolName"]

        school_globals = kamar_api_query("GetGlobals")

        for definition in school_globals.iter("PeriodDefinition"):
            index = definition.attrib["index"]
            name = definition.findtext("PeriodName")
            self.period_names[index] = name

        for day in school_globals.find("StartTimes").iter("Day"):
            day_index = day.attrib["index"]

            self.period_times[day_index] = {}

            for period in day.iter("PeriodTime"):
                period_index = period.attrib["index"]
                period_time_text = period.text

                if period_time_text is None:
                    continue

                period_time = list(map(int, period_time_text.split(":")))

                self.period_times[day_index][self.period_names[period_index]] = period_time
