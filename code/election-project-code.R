library(zoltr)
library(tidyverse)
library(geofacet)
theme_set(theme_bw())


## connect to Zoltar
zoltar_connection <- new_connection()
zoltar_authenticate(zoltar_connection, Sys.getenv("Z_USERNAME"), Sys.getenv("Z_PASSWORD"))

the_projects <- projects(zoltar_connection)
project_url <- the_projects[the_projects$name == "2020 Election Forecasts", "url"]

## number of electoral votes won by dem
ev_won_dem <- do_zoltar_query(zoltar_connection,
    project_url =  project_url,
    is_forecast_query = TRUE,
    targets = "ev_won_dem",
    type=c("point", "quantile"),
    verbose = FALSE) 

med_idx <- which(ev_won_dem$class=="quantile" & ev_won_dem$quantile==0.5)
ev_won_dem[med_idx, "class"] <- "point"

ev_won_quantiles <- ev_won_dem %>%
    select(model, timezero, unit, class, quantile, value) %>%
    filter(class=="quantile", quantile!=0.5) %>%
    pivot_wider(names_from = quantile, values_from=value, names_prefix="q_")

ggplot(ev_won_dem, aes(x=timezero, color=model, fill=model)) +
    geom_point(data=filter(ev_won_dem, class=="point"), alpha=.4, aes(y=value)) + 
    geom_point(data=filter(ev_won_dem, class=="quantile", quantile==0.5), aes(y=value), alpha=.4) +
    geom_smooth(data=filter(ev_won_dem, class=="point"), aes(y=value), se=FALSE, span=.2) + 
    geom_smooth(data=filter(ev_won_dem, class=="quantile", quantile==0.5), aes(y=value), se=FALSE, span=.2) +
    #geom_smooth(se=FALSE, span=.2) +
    geom_ribbon(data=ev_won_quantiles, aes(ymin=q_0.1, ymax=q_0.9), alpha=.1)+
    geom_ribbon(data=ev_won_quantiles, aes(ymin=q_0.05, ymax=q_0.95), alpha=.1)+
    ylab("predicted electoral votes won by democratic candidate") +
    scale_x_date(name="date of prediction", limits=c(as.Date("2020-07-01"), as.Date("2020-11-03"))) +
    geom_hline(yintercept=270, linetype=2)

ggplot(ev_won_dem, aes(x=timezero, color=model, fill=model)) +
    geom_point(data=filter(ev_won_dem, class=="point"), alpha=.4, aes(y=value)) + 
    geom_point(data=filter(ev_won_dem, class=="quantile", quantile==0.5), aes(y=value), alpha=.4) +
    geom_smooth(data=filter(ev_won_dem, class=="point"), aes(y=value), se=FALSE, span=.2) + 
    geom_smooth(data=filter(ev_won_dem, class=="quantile", quantile==0.5), aes(y=value), se=FALSE, span=.2) +
    #geom_smooth(se=FALSE, span=.2) +
    ylab("predicted electoral votes won by democratic candidate") +
    scale_x_date(name="date of prediction") +#, limits=c(as.Date("2020-07-01"), as.Date("2020-11-03"))) +
    geom_hline(yintercept=270, linetype=2)


## electoral vote win prob

ec_win_dem <-  do_zoltar_query(zoltar_connection,
    project_url =  project_url,
    is_forecast_query = TRUE,
    targets = "ec_win_dem",
    type="bin",
    verbose = FALSE)

ggplot(filter(ec_win_dem, cat=="Dem win"), aes(x=timezero, color=model, y=prob)) +
    geom_line() + 
    scale_y_continuous(name="predicted probability of Democratic win", limits=c(0,1)) +
    scale_x_date(name="date of prediction")


## popvote_win_dem

popvote_win_dem <-  do_zoltar_query(zoltar_connection,
    project_url =  project_url,
    is_forecast_query = TRUE,
    targets = "popvote_win_dem",
    type="bin",
    verbose = FALSE)

pv_win_dem <- popvote_win_dem %>%
    filter(cat=="TRUE") %>%
    select(-season, -sample, -quantile, -family, -param1, -param2, -param3, -value) %>%
    separate(unit, into=c("state", "race"), remove=FALSE, extra="merge")

ggplot(filter(pv_win_dem, race=="pres"), aes(x=timezero, color=model, y=prob)) +
    geom_line() + 
    #geom_point(size=1) +
    geom_hline(yintercept=.5, linetype=2) +
    scale_y_continuous(name="predicted probability of Dem win", limits=c(0,1)) +
    scale_x_date(name="date of prediction", limits=c(as.Date("2020-09-01"), as.Date("2020-11-03")))+
    theme(axis.text.x = element_text(angle=90))+
    facet_geo(~ state, grid = "us_state_grid2")
    

close_sen_races <- c("AK", "AL", "AZ", "CO", "GA", "IA", "KS", "KY", "ME", "MI", "MN", "MS", "MT", "NC", "SC", "TX", "TN")
ggplot(filter(pv_win_dem, state %in% close_sen_races, race %in% c("sen", "sen-sp")), aes(x=timezero, color=model, y=prob)) +
    geom_line() + 
    geom_hline(yintercept=.5, linetype=2) +
    scale_y_continuous(name="predicted probability of Democratic win", limits=c(0,1)) +
    scale_x_date(name="date of prediction", limits=c(as.Date("2020-07-01"), as.Date("2020-11-03")) )+
    facet_wrap(.~ unit) +
    scale_color_brewer(palette="Dark2") +
    ggtitle("predicted probability of Democratic win, selected senate races")


