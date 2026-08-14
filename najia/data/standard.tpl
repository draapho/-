{{- gender ~ '测：' ~ title if title else '' -}}
公历：{{solar.year}}年{{solar.month}}月{{solar.day}}日{{solar.hour}}时{{solar.minute}}分
干支：{{lunar.gz5.year}}年　{{lunar.gz5.month}}月　{{lunar.gz5.day}}日　{{lunar.gz5.hour}}时　{{lunar.xkong}}旬空
{# 　　　             申金月　                  申金日　　                震宫　     雷地豫　　   六合　　              坤宫　               坤为地　　              六冲　#}
{{ '　' * 3 }}{{lunar.gz5.month[1:]}}月　{{lunar.gz5.day[1:]}}日　　{{gong}}宫·{{name[:4]}}　{{extra}}{{'　　' ~ (bian.gong ~ '宫·' ~ bian.name[:4] ~ '　' ~ bian.extra ~ '　动化　月日') if bian else '' }}
{# 朱雀　      囚　　　    囚　　　　    妻财       未土               ①                                    ▅▅▅▅▅        应         ｏ        ▅▅　▅▅　        妻财         丑土　                       化进　　        休    #}
{{god6.5}}　{{yaom.5}}{{yaod.5}}　{{qin6.5}}{{qinx.5[-2:]}}{{ hide.numc.5 | default('　', true) }}{{main.mark.5}}{{shiy.5}}{{(dyao.5 ~ bian.mark.5 ~ bian.qin6.5 ~ bian.qinx.5[-2:] ~ ('　' ~ bian.dong.5 ~ bian.yaom.5 if dyao.5 != '　' else '')) if bian else ''}}
{{god6.4}}　{{yaom.4}}{{yaod.4}}　{{qin6.4}}{{qinx.4[-2:]}}{{ hide.numc.4 | default('　', true) }}{{main.mark.4}}{{shiy.4}}{{(dyao.4 ~ bian.mark.4 ~ bian.qin6.4 ~ bian.qinx.4[-2:] ~ ('　' ~ bian.dong.4 ~ bian.yaom.4 if dyao.4 != '　' else '')) if bian else ''}}
{{god6.3}}　{{yaom.3}}{{yaod.3}}　{{qin6.3}}{{qinx.3[-2:]}}{{ hide.numc.3 | default('　', true) }}{{main.mark.3}}{{shiy.3}}{{(dyao.3 ~ bian.mark.3 ~ bian.qin6.3 ~ bian.qinx.3[-2:] ~ ('　' ~ bian.dong.3 ~ bian.yaom.3 if dyao.3 != '　' else '')) if bian else ''}}
{{god6.2}}　{{yaom.2}}{{yaod.2}}　{{qin6.2}}{{qinx.2[-2:]}}{{ hide.numc.2 | default('　', true) }}{{main.mark.2}}{{shiy.2}}{{(dyao.2 ~ bian.mark.2 ~ bian.qin6.2 ~ bian.qinx.2[-2:] ~ ('　' ~ bian.dong.2 ~ bian.yaom.2 if dyao.2 != '　' else '')) if bian else ''}}
{{god6.1}}　{{yaom.1}}{{yaod.1}}　{{qin6.1}}{{qinx.1[-2:]}}{{ hide.numc.1 | default('　', true) }}{{main.mark.1}}{{shiy.1}}{{(dyao.1 ~ bian.mark.1 ~ bian.qin6.1 ~ bian.qinx.1[-2:] ~ ('　' ~ bian.dong.1 ~ bian.yaom.1 if dyao.1 != '　' else '')) if bian else ''}}
{{god6.0}}　{{yaom.0}}{{yaod.0}}　{{qin6.0}}{{qinx.0[-2:]}}{{ hide.numc.0 | default('　', true) }}{{main.mark.0}}{{shiy.0}}{{(dyao.0 ~ bian.mark.0 ~ bian.qin6.0 ~ bian.qinx.0[-2:] ~ ('　' ~ bian.dong.0 ~ bian.yaom.0 if dyao.0 != '　' else '')) if bian else ''}}

{{('伏神　' ~ yaom.11 ~ yaod.11 ~ '　' ~ hide.qin6.5 ~ hide.qinx.5[-2:] ~ hide.numc.5) if hide.numc.5 else '' -}}
{{('伏神　' ~ yaom.10 ~ yaod.10 ~ '　' ~ hide.qin6.4 ~ hide.qinx.4[-2:] ~ hide.numc.4) if hide.numc.4 else '' -}}
{{('伏神　' ~ yaom.9 ~ yaod.9 ~ '　' ~ hide.qin6.3 ~ hide.qinx.3[-2:] ~ hide.numc.3) if hide.numc.3 else '' -}}
{{('伏神　' ~ yaom.8 ~ yaod.8 ~ '　' ~ hide.qin6.2 ~ hide.qinx.2[-2:] ~ hide.numc.2) if hide.numc.2 else '' -}}
{{('伏神　' ~ yaom.7 ~ yaod.7 ~ '　' ~ hide.qin6.1 ~ hide.qinx.1[-2:] ~ hide.numc.1) if hide.numc.1 else '' -}}
{{('伏神　' ~ yaom.6 ~ yaod.6 ~ '　' ~ hide.qin6.0 ~ hide.qinx.0[-2:] ~ hide.numc.0) if hide.numc.0 else ''}}

互卦「{{hu.name}}」　错卦「{{cuo.name}}」　综卦「{{zong.name}}」

{{- guaci_text if guaci else '' -}}
