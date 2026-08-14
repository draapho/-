{{- gender ~ '测：' ~ title if title else '' -}}
公历：{{solar.year}}年{{solar.month}}月{{solar.day}}日{{solar.hour}}时{{solar.minute}}分
干支：{{lunar.gz5.year}}年　{{lunar.gz5.month}}月　{{lunar.gz5.day}}日　{{lunar.gz5.hour}}时　{{lunar.xkong}}旬空

{{ '　' * 3 }}{{lunar.gz5.month[1:]}}月　{{lunar.gz5.day[1:]}}日　　{{extra}}　{{gong}}宫　{{name}}{{ ('　　　' ~bian.name ~ '　' ~ bian.gong ~ '宫 ' ~ bian.extra ~ '动化　　月日') if bian and bian.name else '' }}
{{god6.5}}{{ '　' * 10 }}{{qin6.5}}{{qinx.5}}{{ hide.numc.5 | default('　', true) }}{{main.mark.5}}{{shiy.5}}{{dyao.5}}　{{bian.mark.5}}　{{bian.qin6.5}}
{{god6.4}}{{ '　' * 10 }}{{qin6.4}}{{qinx.4}}{{ hide.numc.4 | default('　', true) }}{{main.mark.4}}{{shiy.4}}{{dyao.4}}　{{bian.mark.4}}　{{bian.qin6.4}}
{{god6.3}}{{ '　' * 10 }}{{qin6.3}}{{qinx.3}}{{ hide.numc.3 | default('　', true) }}{{main.mark.3}}{{shiy.3}}{{dyao.3}}　{{bian.mark.3}}　{{bian.qin6.3}}
{{god6.2}}{{ '　' * 10 }}{{qin6.2}}{{qinx.2}}{{ hide.numc.2 | default('　', true) }}{{main.mark.2}}{{shiy.2}}{{dyao.2}}　{{bian.mark.2}}　{{bian.qin6.2}}
{{god6.1}}{{ '　' * 10 }}{{qin6.1}}{{qinx.1}}{{ hide.numc.1 | default('　', true) }}{{main.mark.1}}{{shiy.1}}{{dyao.1}}　{{bian.mark.1}}　{{bian.qin6.1}}
{{god6.0}}{{ '　' * 10 }}{{qin6.0}}{{qinx.0}}{{ hide.numc.0 | default('　', true) }}{{main.mark.0}}{{shiy.0}}{{dyao.0}}　{{bian.mark.0}}　{{bian.qin6.0}}
{{('伏' ~ hide.numc.5 ~ ('　' * 10) ~ hide.qin6.5) if hide.numc.5 else '' -}}
{{('伏' ~ hide.numc.4 ~ ('　' * 10) ~ hide.qin6.4) if hide.numc.4 else '' -}}
{{('伏' ~ hide.numc.3 ~ ('　' * 10) ~ hide.qin6.3) if hide.numc.3 else '' -}}
{{('伏' ~ hide.numc.2 ~ ('　' * 10) ~ hide.qin6.2) if hide.numc.2 else '' -}}
{{('伏' ~ hide.numc.1 ~ ('　' * 10) ~ hide.qin6.1) if hide.numc.1 else '' -}}
{{('伏' ~ hide.numc.0 ~ ('　' * 10) ~ hide.qin6.0) if hide.numc.0 else ''}}

互卦「{{hu.name}}」　错卦「{{cuo.name}}」　综卦「{{zong.name}}」

{{- guaci_text if guaci else '' -}}
