const Header = () => {
  return (
    <header className="px-4 lg:px-6 py-3 border-b border-border/50 bg-card/50 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
          <span className="text-primary font-display font-bold text-lg">C</span>
        </div>
        <div>
          <h1 className="font-display font-bold text-lg text-foreground">Conscience</h1>
          <p className="text-xs text-muted-foreground">Your Personal Wellness Companion</p>
        </div>
      </div>
    </header>
  );
};

export default Header;