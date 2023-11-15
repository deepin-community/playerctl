/*
 * This file is part of playerctl.
 *
 * playerctl is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Lesser General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option)
 * any later version.
 *
 * playerctl is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
 * more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with playerctl If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright © 2014, Tony Crisci and contributors
 */

#ifndef __PLAYERCTL_PLAYER_PRIVATE_H__
#define __PLAYERCTL_PLAYER_PRIVATE_H__

#include "playerctl-player.h"

char *pctl_player_get_instance(PlayerctlPlayer *player);

gint player_name_string_compare_func(gconstpointer a, gconstpointer b, gpointer user_data);

gint player_name_compare_func(gconstpointer a, gconstpointer b, gpointer user_data);

gint player_compare_func(gconstpointer a, gconstpointer b, gpointer user_data);

#endif /* __PLAYERCTL_PLAYER_PRIVATE_H__ */
