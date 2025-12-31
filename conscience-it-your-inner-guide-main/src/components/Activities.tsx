import React from 'react';
import { useActivities } from '@/contexts/ActivityContext';
import { Clock, Play, Star, Wind, Zap, Brain, Activity, Palette, Users } from 'lucide-react';
import { ACTIVITY_CATEGORIES } from '@/types/activities';

const Activities: React.FC = () => {
  const { filteredActivities, featuredActivity, loading, startActivity } = useActivities();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const getCategoryIcon = (categoryId: string) => {
    const category = ACTIVITY_CATEGORIES.find(c => c.id === categoryId);
    const iconMap = {
      'Wind': Wind,
      'Zap': Zap,
      'Brain': Brain,
      'Activity': Activity,
      'Palette': Palette,
      'Users': Users
    };
    const IconComponent = iconMap[category?.icon as keyof typeof iconMap] || Brain;
    return <IconComponent className="w-5 h-5" />;
  };

  const getCategoryColor = (categoryId: string) => {
    const category = ACTIVITY_CATEGORIES.find(c => c.id === categoryId);
    const colorMap = {
      'blue': 'text-blue-400',
      'green': 'text-green-400',
      'purple': 'text-purple-400',
      'orange': 'text-orange-400',
      'pink': 'text-pink-400',
      'teal': 'text-teal-400'
    };
    return colorMap[category?.color as keyof typeof colorMap] || 'text-purple-400';
  };

  return (
    <div className="space-y-6">
      {/* Featured Activity */}
      {featuredActivity && (
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-primary/10 rounded-2xl blur-xl"></div>
          <div className="relative backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 animate-pulse-glow hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-xl bg-primary/20 ${getCategoryColor(featuredActivity.category)}`}>
                {getCategoryIcon(featuredActivity.category)}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs font-medium text-yellow-400">Featured</span>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">{featuredActivity.title}</h3>
                <p className="text-muted-foreground text-sm mb-4">{featuredActivity.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{featuredActivity.duration} min</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className={`px-2 py-1 rounded-full bg-primary/10 text-primary`}>
                        {featuredActivity.difficulty}
                      </span>
                    </div>
                    {featuredActivity.vrEnabled && (
                      <span className="px-2 py-1 rounded-full bg-purple-500/20 text-purple-400">
                        VR
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => startActivity(featuredActivity.id)}
                    className="px-4 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Start
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Activity Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredActivities.map((activity) => (
          <div
            key={activity.id}
            className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 hover:scale-[1.02] transition-all duration-300 group cursor-pointer"
            onClick={() => startActivity(activity.id)}
          >
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg bg-primary/10 ${getCategoryColor(activity.category)}`}>
                {getCategoryIcon(activity.category)}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-foreground mb-1 group-hover:text-primary transition-colors">
                  {activity.title}
                </h4>
                <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
                  {activity.description}
                </p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{activity.duration}m</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full bg-muted/50 text-muted-foreground`}>
                    {activity.difficulty}
                  </span>
                  {activity.vrEnabled && (
                    <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400">
                      VR
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredActivities.length === 0 && (
        <div className="text-center py-12">
          <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No activities available right now.</p>
        </div>
      )}
    </div>
  );
};

export default Activities;
