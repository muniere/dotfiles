#
# Constants
#
VERBOSE = true
NOOP = false

CONFIGS = {
  :bash => [
    { :src => 'sh.d'     , :dst => '.sh.d'      },
    { :src => 'bash.d'   , :dst => '.bash.d'    }
  ],
  :zsh  => [
    { :src => 'sh.d'     , :dst => '.sh.d'      },
    { :src => 'zsh.d'    , :dst => '.zsh.d'     }
  ],
  :vim  => [
    { :src => 'vimrc'    , :dst => '.vimrc'     },
    { :src => 'vim.d'    , :dst => '.vim.d'     },
    { :src => 'vim'      , :dst => '.vim'       , :extra => Proc.new { Helper.git_clone(NEOBUNDLE[:src], NEOBUNDLE[:dst]) } }
  ],
  :tmux => [
    { :src => 'tmux.conf', :dst => '.tmux.conf' }
  ],
  :tig  => [
    { :src => 'tigrc'    , :dst => '.tigrc'     }
  ],
  :peco => [
    { :src => 'peco'     , :dst => '.peco'      }
  ]
}

PACKAGES = CONFIGS.keys

SYSTEMS = [
  { :keyword => /ubuntu/i, :name => 'ubuntu' },
  { :keyword => /debian/i, :name => 'debian' },
  { :keyword => /centos/i, :name => 'centos' },
  { :keyword => /darwin/i, :name => 'macos'  },
  { :keyword => /amzn/i  , :name => 'amazon' }
]

NEOBUNDLE = {
  :src => 'https://github.com/Shougo/neobundle.vim',
  :dst => File.join(ENV['HOME'], '/.vim/bundle/neobundle.vim')
}

#
# Extended String
#
class String
  def red;     "\033[31m#{self}\033[0m"; end
  def green;   "\033[32m#{self}\033[0m"; end
  def yellow;  "\033[33m#{self}\033[0m"; end
  def blue;    "\033[34m#{self}\033[0m"; end
  def magenta; "\033[35m#{self}\033[0m"; end
  def cyan;    "\033[36m#{self}\033[0m"; end
  def gray;    "\033[37m#{self}\033[0m"; end
end

#
# Helper functions
#
class Helper

  #
  # output info
  #
  def self.info(message)
    STDERR.puts "[INFO] #{message}".cyan if VERBOSE
  end

  #
  # output warn
  #
  def self.warn(message)
    STDERR.puts "[WARN] #{message}".yellow if VERBOSE
  end

  #
  # get system name
  #
  def self.sysname
    uname = File.file?('/etc/issue') ? File.read('/etc/issue') : %x(uname -a).strip
    system = SYSTEMS.find { |sys| sys[:keyword] =~ uname }

    return !system.nil? ? system[:name] : nil
  end

  #
  # list files in directory
  #
  def self.lsdir(dir)
    return Dir.entries(dir) - ['.', '..']
  end

  #
  # make directory
  #
  def self.mkdir(dir)
    return self.exec("mkdir #{dir}")
  end

  #
  # make directory recursively
  #
  def self.mkdir_p(dir)
    return self.exec("mkdir -p #{dir}")
  end

  #
  # remove file
  #
  def self.rm(file)
    return self.exec("rm #{file}")
  end

  #
  # remove file recursively
  #
  def self.rm_r(dir)
    return self.exec("rm -r #{dir}")
  end

  #
  # create symlink
  #
  def self.symlink(src, dst)
    return self.exec("ln -s #{src} #{dst}")
  end

  #
  # create symlink forcely
  #
  def self.symlink_f(src, dst)
    return self.exec("ln -sf #{src} #{dst}")
  end

  #
  # create symlink recursively
  #
  def self.symlink_r(src, dst, recursive=true)

    if !File.exists?(src)
      self.warn("File NOT FOUND: #{src}")
      return false
    end

    if File.symlink?(dst)
      self.info("File already exists: #{dst}")
      return true
    end

    # file
    if File.file?(src) 
      return self.symlink_f(src, dst)
    end

    # directory: non-recursive
    if !recursive
      return self.symlink_f(src, dst)
    end

    # directory: recursive
    if !File.directory?(dst)
      self.mkdir_p(dst) 
    end

    success = true

    self.lsdir(src).each do |conf|
      success &= self.symlink_r(File.join(src, conf), File.join(dst, conf), recursive=false)
    end

    return success
  end

  #
  # unlink recursively
  #
  def self.unlink_r(target)

    if !File.exists?(target) and !File.symlink?(target)
      self.info("File already removed: #{target}")
      return true
    end

    # symlink
    if File.symlink?(target)
      return self.rm(target)
    end

    # file
    if File.file?(target)
      self.info("File is NOT LINK: #{target}")
      return false
    end

    # directory
    success = true

    self.lsdir(target).each do |file|
      path = File.join(target, file)

      next if !File.symlink?(path)

      success &= self.rm(path)
    end

    if self.lsdir(target).empty?
      success &= self.rm_r(target)
    end

    return success
  end

  #
  # git clone
  #
  def self.git_clone(src=nil, dst=nil)

    return true if File.directory?(dst)

    return self.exec("git clone #{src} #{dst}")
  end

  #
  # concat two files
  #
  def self.concat(src=nil, dst=nil)
    return self.exec("cat #{src} >> #{dst}")
  end

  #
  # exec shell command
  #
  def self.exec(command, options={})
    if (options[:verbose].nil? ? VERBOSE : options[:verbose])
      STDERR.puts "[EXEC] #{command}".green 
    end

    return true if (options[:noop].nil? ? NOOP : options[:noop])
    return Kernel.system(command)
  end
end

#
# Actions
#
class Action

  #
  # deploy config file
  #
  def self.deploy(config, system=nil)
    if system.nil?
      success = false
      success |= self.deploy(config, Helper.sysname) 
      success |= self.deploy(config, 'default')
      return success
    end

    return Helper.symlink_r(File.join(Dir.pwd, system, config[:src]), File.join(ENV['HOME'], config[:dst]))
  end

  #
  # undeploy config file
  #
  def self.undeploy(config)
    target = File.join(ENV['HOME'], config[:dst])

    return Helper.unlink_r(target)
  end

  #
  # install config for package
  #
  def self.install(package)

    return false unless PACKAGES.include?(package)

    # deploy
    success = true

    CONFIGS[package].each do |conf|
      success &= self.deploy(conf)

      if conf[:extra].is_a?(Proc)
        conf[:extra].call
      end
    end

    return success
  end

  #
  # uninstall config for package
  #
  def self.uninstall(package)

    return false unless PACKAGES.include?(package)

    # undeploy
    success = true

    CONFIGS[package].each do |conf|
      success &= self.undeploy(conf)
    end

    return success
  end

  #
  # show status of config
  #
  def self.status

    success = true

    (confs = CONFIGS.values.flatten.map{ |conf| conf[:dst] }.uniq.sort).each do |conf| 
      path = File.join(ENV['HOME'], conf)

      next if !File.exists?(path)

      command = (Helper.sysname == 'macos') ? "ls -lFG #{path}" : "ls -lFo #{path}"

      success &= Helper.exec(command, :verbose => true, :noop => false)

      puts if conf != confs.last 
    end

    return success
  end

  #
  # inject template into rc files
  #
  def self.inject

    Dir.glob('./default/tmpl.d/*').each do |tmpl|
      src = tmpl
      dst = File.join(ENV['HOME'], '.' + File.basename(tmpl))

      if File.exists?(dst) and File.read(dst).include?(File.read(src))
        Helper.info("File already setup: #{dst}")
        next
      end

      Helper.concat(src, dst)
    end
  end
end

#
# Tasks
#
desc 'install'
task :install do
  PACKAGES.each do |package|
    Action.install(package)
  end
  Action.inject
end

desc 'uninstall'
task :uninstall do
  PACKAGES.each do |package|
    Action.uninstall(package)
  end
end

desc 'show status'
task :status do
  Action.status
end

# vim: ft=ruby sw=2 ts=2 sts=2
