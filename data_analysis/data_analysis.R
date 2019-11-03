rm(list=ls())
setwd("~/Desktop/MultiAgentSystems/data_analysis")
library(checkpoint)
checkpoint("2019-10-29")

library(ggplot2)

# info - false , fire - 1,1
dat1 <- read.csv("./info_false_fire_1", header=TRUE)
dat2 <- read.csv("./info_true_fire_1", header=TRUE)
dat3 <- read.csv("./info_false_fire_47_15", header=TRUE)
dat4 <- read.csv("./info_true_fire_47_15", header=TRUE)

# join the data
data_all <- do.call("rbind", list(dat1, dat2, dat3, dat4))

# add K to N
data_all$N <- as.numeric(data_all$N) + as.numeric(data_all$K)

# extract average alive civilians
mean_alive <- aggregate(data_all$Agents.saved, by=list(data_all$N, data_all$K, data_all$fire_x, data_all$civil_info_exchange), mean)
sd_alive <- aggregate(data_all$Agents.saved, by=list(data_all$N, data_all$K, data_all$fire_x, data_all$civil_info_exchange), sd)
alive_civilians <- mean_alive
alive_civilians$sd <- sd_alive$x

colnames(alive_civilians) <- c("num_civilians", "num_stewards", "fire_x", "info_exchange", "mean", "sd")
alive_civilians

# Plot mean alive as a function of civilians and group of stewards for each fire position and each info exchange.
fire_1_true <- alive_civilians[which(alive_civilians$fire_x==1 & alive_civilians$info_exchange=="True"),]
fire_1_true

ggplot(fire_1_true ,aes(x=num_civilians, y=mean)) +
  geom_point(aes(colour=num_stewards), size=2.5) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd), colour="red", width=.3) +
  theme(text = element_text(size=15)) +
  labs(x="Number of agents", y=paste("Average number of agents alive"), col="Number of stewards") +
  ggtitle("Fire starts at (1,1) - Civilians Exchange Information")


fire_1_false <- alive_civilians[which(alive_civilians$fire_x==1 & alive_civilians$info_exchange=="False"),]
fire_1_false

ggplot(fire_1_false ,aes(x=num_civilians, y=mean)) +
  geom_point(aes(colour=num_stewards), size=2.5) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd), colour="red", width=.3) +
  theme(text = element_text(size=15)) +
  labs(x="Number of agents", y=paste("Average number of agents alive"), col="Number of stewards") +
  ggtitle("Fire starts at (1,1) - Civilians Don't Exchange Information")

fire_47_true <- alive_civilians[which(alive_civilians$fire_x==47 & alive_civilians$info_exchange=="True"),]
fire_47_true

ggplot(fire_47_true ,aes(x=num_civilians, y=mean)) +
  geom_point(aes(colour=num_stewards), size=2.5) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd), colour="red", width=.3) +
  theme(text = element_text(size=15)) +
  labs(x="Number of agents", y=paste("Average number of agents alive"), col="Number of stewards") +
  ggtitle("Fire starts at (47,15) - Civilians Exchange Information")

fire_47_false <- alive_civilians[which(alive_civilians$fire_x==47 & alive_civilians$info_exchange=="False"),]
fire_47_false

ggplot(fire_47_false ,aes(x=num_civilians, y=mean)) +
  geom_point(aes(colour=num_stewards), size=2.5) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd), colour="red", width=.3) +
  theme(text = element_text(size=15)) +
  labs(x="Number of agents", y=paste("Average number of agents alive"), col="Number of stewards") +
  ggtitle("Fire starts at (47,15) - Civilians Don't Exchange Information")

