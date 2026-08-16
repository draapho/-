{{- gender ~ '测：' ~ title if title else '' -}}
干支：{{lunar.gz5.year}}·{{lunar.gz5.month[:4]}}·{{lunar.gz5.day[:4]}}·{{lunar.gz5.hour}}·{{lunar.xkong}}旬空
公历：{{solar.year}}年{{solar.month}}月{{solar.day}}日{{solar.hour}}时{{solar.minute}}分　官鬼-父母-兄弟-子孙-妻财-
{# 注释行:     申金月　                  申金日　　                震宫　     雷地豫　　   六合　　              坤宫　               坤为地　　              六冲　#}
{{ '　' * 3 }}{{lunar.gz5.month[1:]}}{{lunar.gz5.day[1:]}}　{{gong}}宫·{{name[:4]}}　{{extra}}{{'　' * 3 ~ (bian.gong ~ '宫·' ~ bian.name[:4] ~ '　' ~ bian.extra ~ '　动化　' ~ lunar.gz5.month[1:4] ~　'　' ~ lunar.gz5.day[1:4]) if bian else '' }}
{# 朱雀　      囚　　　    囚　　　　    妻财       未土               ①                               ▅▅▅▅▅      冲/合       应         ｏ      ▅▅　▅▅　        妻财         丑土　                       化进　　        休    #}
{{god6.5}}　{{yaom.5}}{{yaod.5}}　{{qin6.5}}{{qinx.5[-2:]}}{{ hide.numc.5 | default('　', true) }}{{main.mark.5}}{{chohe.5}}{{shiy.5}}{{(dyao.5 ~ bian.mark.5 ~ bian.qin6.5 ~ bian.qinx.5[-2:] ~ ('　' ~ bian.dong.5 ~ bian.yaom.5 ~ bian.yaod.5 if dyao.5 != '　' else '')) if bian else ''}}
{{god6.4}}　{{yaom.4}}{{yaod.4}}　{{qin6.4}}{{qinx.4[-2:]}}{{ hide.numc.4 | default('　', true) }}{{main.mark.4}}{{chohe.4}}{{shiy.4}}{{(dyao.4 ~ bian.mark.4 ~ bian.qin6.4 ~ bian.qinx.4[-2:] ~ ('　' ~ bian.dong.4 ~ bian.yaom.4 ~ bian.yaod.4 if dyao.4 != '　' else '')) if bian else ''}}
{{god6.3}}　{{yaom.3}}{{yaod.3}}　{{qin6.3}}{{qinx.3[-2:]}}{{ hide.numc.3 | default('　', true) }}{{main.mark.3}}{{chohe.3}}{{shiy.3}}{{(dyao.3 ~ bian.mark.3 ~ bian.qin6.3 ~ bian.qinx.3[-2:] ~ ('　' ~ bian.dong.3 ~ bian.yaom.3 ~ bian.yaod.3 if dyao.3 != '　' else '')) if bian else ''}}
{{god6.2}}　{{yaom.2}}{{yaod.2}}　{{qin6.2}}{{qinx.2[-2:]}}{{ hide.numc.2 | default('　', true) }}{{main.mark.2}}{{chohe.2}}{{shiy.2}}{{(dyao.2 ~ bian.mark.2 ~ bian.qin6.2 ~ bian.qinx.2[-2:] ~ ('　' ~ bian.dong.2 ~ bian.yaom.2 ~ bian.yaod.2 if dyao.2 != '　' else '')) if bian else ''}}
{{god6.1}}　{{yaom.1}}{{yaod.1}}　{{qin6.1}}{{qinx.1[-2:]}}{{ hide.numc.1 | default('　', true) }}{{main.mark.1}}{{chohe.1}}{{shiy.1}}{{(dyao.1 ~ bian.mark.1 ~ bian.qin6.1 ~ bian.qinx.1[-2:] ~ ('　' ~ bian.dong.1 ~ bian.yaom.1 ~ bian.yaod.1 if dyao.1 != '　' else '')) if bian else ''}}
{{god6.0}}　{{yaom.0}}{{yaod.0}}　{{qin6.0}}{{qinx.0[-2:]}}{{ hide.numc.0 | default('　', true) }}{{main.mark.0}}{{chohe.0}}{{shiy.0}}{{(dyao.0 ~ bian.mark.0 ~ bian.qin6.0 ~ bian.qinx.0[-2:] ~ ('　' ~ bian.dong.0 ~ bian.yaom.0 ~ bian.yaod.0 if dyao.0 != '　' else '')) if bian else ''}}
{{ ('　' * 19 ~ '飞神') if (hide.numc.0 or hide.numc.1 or hide.numc.2 or hide.numc.3 or hide.numc.4 or hide.numc.5) else '' }}
{{('伏' ~ hide.numc.5 ~ '　' ~ hide.yaom.5 ~ hide.yaod.5 ~ '　' ~ hide.qin6.5 ~ hide.qinx.5[-2:] ~ hide.numc.5 ~ '　' * 2 ~ hide.fei.5 ~ '\n') if hide.numc.5 else '' -}}
{{('伏' ~ hide.numc.4 ~ '　' ~ hide.yaom.4 ~ hide.yaod.4 ~ '　' ~ hide.qin6.4 ~ hide.qinx.4[-2:] ~ hide.numc.4 ~ '　' * 2 ~ hide.fei.4 ~ '\n') if hide.numc.4 else '' -}}
{{('伏' ~ hide.numc.3 ~ '　' ~ hide.yaom.3 ~ hide.yaod.3 ~ '　' ~ hide.qin6.3 ~ hide.qinx.3[-2:] ~ hide.numc.3 ~ '　' * 2 ~ hide.fei.3 ~ '\n') if hide.numc.3 else '' -}}
{{('伏' ~ hide.numc.2 ~ '　' ~ hide.yaom.2 ~ hide.yaod.2 ~ '　' ~ hide.qin6.2 ~ hide.qinx.2[-2:] ~ hide.numc.2 ~ '　' * 2 ~ hide.fei.2 ~ '\n') if hide.numc.2 else '' -}}
{{('伏' ~ hide.numc.1 ~ '　' ~ hide.yaom.1 ~ hide.yaod.1 ~ '　' ~ hide.qin6.1 ~ hide.qinx.1[-2:] ~ hide.numc.1 ~ '　' * 2 ~ hide.fei.1 ~ '\n') if hide.numc.1 else '' -}}
{{('伏' ~ hide.numc.0 ~ '　' ~ hide.yaom.0 ~ hide.yaod.0 ~ '　' ~ hide.qin6.0 ~ hide.qinx.0[-2:] ~ hide.numc.0 ~ '　' * 2 ~ hide.fei.0 ~ '\n') if hide.numc.0 else '' -}}

{{('注㊀　' ~ desche3 ~ '\n') if desche3 else '' -}}
{{('注㊁　' ~ descxing3 ~ '\n') if descxing3 else '' -}}

{{'\n互卦「' ~ hu.name ~ '」　错卦「' ~ cuo.name ~ '」　综卦「' ~ zong.name ~ '」'}}

{{(guaci_text) if guaci else ''}}