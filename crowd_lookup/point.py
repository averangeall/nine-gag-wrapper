# Recomm:

#     how many points will a user query/hate affect a keyword?
USER_RECOMM_VAL_POINT = 0.9

#     how many points will an admin query/hate affect a keyword?
ADMIN_RECOMM_VAL_POINT = 4.5

#     how many points required to be visible to everyone?
MIN_RECOMM_VISIBLE_POINT = 1.5


# Explain:

#     how many points will a user like/hate affect a explain?
USER_EXPL_VAL_POINT = 0.9

#     how many points will an admin like/hate affect a explain?
ADMIN_EXPL_VAL_POINT = 4.5

#     how many points required to be visible to everyone?
MIN_EXPL_VISIBLE_POINT = 0.0

#     what is the initial point of a explain from a user?
USER_EXPL_INIT_POINT = 2.0

#     what is the initial point of a explain from a user?
ADMIN_EXPL_INIT_POINT = 5.0

#     how many points will be decreased if one hate his/her own expl?
SELF_HATE_EXPL_POINT = 20.0

#     what is the maximum initial point of a explain from google translate?
GT_SINGLE_EXPL_INIT_POINT = 1.4
GT_MULTIPLE_EXPL_INIT_POINT = 0.5

#     what is the maximum initial point of a explain from urban dictionary?
UD_NO_GT_EXPL_INIT_POINT = 1.2
UD_WITH_GT_EXPL_INIT_POINT = 0.8

#     what is the maximum initial point of a explain from google image?
GI_EXPL_INIT_POINT = 1.0

#     what is the maximum initial point of a explain from urban dictionary?
YT_EXPL_INIT_POINT = 0.7

