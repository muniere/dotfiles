#
# Constants
#
VERBOSE = true
NOOP = false

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

DOTFILES = [
  { :src => 'sh.d'     , :dst => '.sh.d'      },
  { :src => 'bash.d'   , :dst => '.bash.d'    },
  { :src => 'zsh.d'    , :dst => '.zsh.d'     },
  { :src => 'tmux.conf', :dst => '.tmux.conf' },
  { :src => 'tigrc'    , :dst => '.tigrc'     },
  { :src => 'peco'     , :dst => '.peco'      },
  { :src => 'vimrc'    , :dst => '.vimrc'     },
  { :src => 'vim.d'    , :dst => '.vim.d'     },
  { :src => 'vim'      , :dst => '.vim'       ,
    :extra => Proc.new { Helper.git_clone(NEOBUNDLE[:src], NEOBUNDLE[:dst]) } },
]

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
  # output error
  #
  def self.error(message)
    STDERR.puts "[ERROR] #{message}".red
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
  # detect command path
  #
  def self.which(cmd)
    return !(path = %x(which #{cmd})).empty? ? path.strip : nil
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
# Dotfile actions
#
class Dotfile

  #
  # deploy dotfile
  #
  def self.deploy(dotfile, env=nil)
    if env.nil?
      self.deploy(dotfile, Helper.sysname) 
      self.deploy(dotfile, 'default')
      return
    end

    src = File.join(Dir.pwd, env, dotfile[:src])
    dst = File.join(ENV['HOME'], dotfile[:dst])

    # check
    return if !File.exists?(src)

    # symlink
    if File.symlink?(dst)
      Helper.info("File already exists: #{dst}")
      return
    end

    # file
    if File.file?(src) 
      Helper.symlink_f(src, dst)
      return
    end

    # directory
    if !File.directory?(dst)
      Helper.mkdir_p(dst) 
    end

    Helper.lsdir(src).each do |conf|
      s = File.join(src, conf)
      d = File.join(dst, conf)

      if File.exists?(d)
        Helper.info("File already exists: #{d}")
        next
      end

      Helper.symlink_f(s, d)
    end
  end

  #
  # undeploy dotfile
  #
  def self.undeploy(dotfile, env=nil)
    if env.nil?
      self.undeploy(dotfile, Helper.sysname) 
      self.undeploy(dotfile, 'default')
      return
    end
    
    src = File.join(Dir.pwd, env, dotfile[:src])
    dst = File.join(ENV['HOME'], dotfile[:dst])

    # check
    return if !File.exists?(src)

    if !File.exists?(dst) and !File.symlink?(dst)
      Helper.info("File already removed: #{dst}")
      return
    end

    # symlink
    if File.symlink?(dst)
      Helper.rm(dst)
      return
    end

    # file
    if File.file?(dst)
      Helper.info("File is NOT LINK: #{dst}")
      return
    end

    # directory
    Helper.lsdir(src).each do |file|
      d = File.join(dst, file)

      if !File.exists?(d) and !File.symlink?(d)
        Helper.info("File already removed: #{d}")
        return
      end

      if !File.symlink?(d)
        Helper.info("File is NOT LINK: #{d}")
        next
      end

      Helper.rm(d)
    end

    if Helper.lsdir(dst).empty?
      Helper.rm_r(dst)
    end
  end

  #
  # install dotfile
  #
  def self.install(dotfile)

    self.deploy(dotfile)

    if dotfile[:extra].is_a?(Proc)
      dotfile[:extra].call
    end
  end

  #
  # uninstall dotfile
  #
  def self.uninstall(dotfile)
    self.undeploy(dotfile)
  end

  #
  # show status of config
  #
  def self.status

    (files = DOTFILES.map{ |dotfile| dotfile[:dst] }.uniq.sort).each do |file| 
      next if !File.exists?(path = File.join(ENV['HOME'], file))

      Helper.exec((Helper.sysname == 'macos') ? "ls -lFG #{path}" : "ls -lFo #{path}",
                  :verbose => true, :noop => false)

      puts if file != files.last 
    end
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
# Homebrew actions
#
class Homebrew

  #
  # install kegs based on Brewfile
  #
  def self.install

    our_kegs = []
    his_kegs = %x(brew list).lines.map{ |line| line.strip }

    self.kegs.each do |keg| 
      if his_kegs.include?(File.basename(keg)) 
        Helper.info("Keg already installed: #{keg}")
      else
        our_kegs.push(keg)
      end
    end

    if !our_kegs.empty?
      Helper.exec("brew install #{our_kegs.join(' ')}")
    end
  end

  #
  # uninstall kegs based on Brewfile
  #
  def self.uninstall

    our_kegs = []
    his_kegs = %x(brew list).lines.map{ |line| line.strip }

    self.kegs.each do |keg| 
      if !his_kegs.include?(File.basename(keg)) 
        Helper.info("Keg not installed: #{keg}")
      else
        our_kegs.push(File.basename(keg))
      end
    end

    if !our_kegs.empty?
      Helper.exec("brew uninstall #{our_kegs.join(' ')}")
    end
  end

  private
  def self.kegs

    if Helper.which(command = 'brew').nil?
      Helper.error("Command not found: #{command}")
      exit 1
    end

    if !File.exists?(brewfile = File.join(Helper.sysname, 'Brewfile'))
      Helper.error("File not found: #{brewfile}")
      exit 1
    end

    return File.read(brewfile).lines.map{ |line| line.strip }
  end
end

class RubyGem

  #
  # install gems based on Gemfile
  #
  def self.install

    gems = []
    self.gems.each do |gem| 
      if system("gem which #{gem} &>/dev/null") 
        Helper.info("Gem already installed: #{gem}")
      else
        gems.push(gem)
      end
    end

    if !gems.empty?
      Helper.exec("gem install #{gems.join(' ')}")
    end
  end

  #
  # uninstall gems based on Gemfile
  #
  def self.uninstall

    gems = []
    self.gems.each do |gem| 
      if !system("gem which #{gem} &>/dev/null") 
        Helper.info("Gem not installed: #{gem}")
      else
        gems.push(gem)
      end
    end

    if !gems.empty?
      Helper.exec("gem uninstall #{gems.join(' ')}")
    end
  end

  private
  def self.gems

    if Helper.which(command = 'gem').nil?
      Helper.error("Command not found: #{command}")
      exit 1
    end

    if !File.exists?(gemfile = File.join(Helper.sysname, 'Gemfile'))
      Helper.error("File not found: #{gemfile}")
      exit 1
    end

    return File.read(gemfile).lines.select{ |line| line.match(/^gem/) }.map{ |line|
      line.match(/^gem\s+["']([^"']+)["']/)[1] 
    }
  end
end


class Npm

  #
  # install npm packages based on packages.json
  #
  def self.install

    packages = []
    self.packages.each do |package| 
      if system("npm ls -g #{package} &>/dev/null") 
        Helper.info("Package already installed: #{package}")
      else
        packages.push(package)
      end
    end

    if !packages.empty?
      Helper.exec("npm -g install #{packages.join(' ')}")
    end
  end

  #
  # uninstall npm packages based on packages.json
  #
  def self.uninstall

    packages = []
    self.packages.each do |package| 
      if !system("npm ls -g #{package} &>/dev/null") 
        Helper.info("Package not installed: #{package}")
      else
        packages.push(package)
      end
    end

    if !packages.empty?
      Helper.exec("npm -g uninstall #{packages.join(' ')}")
    end
  end

  private
  def self.packages

    if Helper.which(command = 'npm').nil?
      Helper.error("Command not found: #{command}")
      exit 1
    end

    if !File.exists?(package_json = File.join(Helper.sysname, 'package.json'))
      Helper.error("File not found: #{package_json}")
      exit 1
    end

    require 'json'

    return JSON.parse(File.read(package_json))['dependencies'].keys
  end
end

#
# Tasks
#
desc 'install dotfiles'
task :install do
  DOTFILES.each do |dotfile|
    Dotfile.install(dotfile)
  end
  Dotfile.inject
end

desc 'uninstall dotfiles'
task :uninstall do
  DOTFILES.each do |dotfile|
    Dotfile.uninstall(dotfile)
  end
end

desc 'show dotfiles status'
task :status do
  Dotfile.status
end

namespace :x do

  namespace :brew do

    desc 'install brew kegs'
    task :install do
      Homebrew.install
    end

    desc 'uninstall brew kegs'
    task :uninstall do
      Homebrew.uninstall
    end
  end

  namespace :gem do

    desc 'install gems'
    task :install do
      RubyGem.install
    end

    desc 'uninstall gems'
    task :uninstall do
      RubyGem.uninstall
    end
  end

  namespace :npm do

    desc 'install npm packages'
    task :install do
      Npm.install
    end

    desc 'uninstall npm packages'
    task :uninstall do
      Npm.uninstall
    end
  end
end

# vim: ft=ruby sw=2 ts=2 sts=2
